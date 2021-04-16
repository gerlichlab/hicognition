"""Pipeline steps for redis queue"""
import os
import uuid
import logging

from flask.globals import current_app
import pandas as pd
import numpy as np
from ngs import HiCTools as HT
import cooler
from hicognition import io_helpers
import bbi
from .api.helpers import remove_safely
from rq import get_current_job
from . import db
from .models import (
    Dataset,
    Intervals,
    AverageIntervalData,
    Task,
    IndividualIntervalData,
)

# get logger
log = logging.getLogger("rq.worker")


def bed_preprocess_pipeline_step(dataset_id, windowsize):
    """
    Performs bedpe preprocessing pipeline step:
    * run clodius on bedpe file
    * upload result to higlass
    * add Intervals dataset entry
    """
    log.info(f"  Converting to bedpe: {dataset_id} with {windowsize}")
    # get database object
    dataset = Dataset.query.get(dataset_id)
    file_path = dataset.file_path
    # generate bedpe file
    bedpe_file = file_path + f".{windowsize}" + ".bedpe"
    io_helpers.convert_bed_to_bedpe(file_path, bedpe_file, windowsize)
    # interval generation succeeded, commit to database
    new_entry = Intervals(
        dataset_id=dataset_id,
        name=bedpe_file.split(os.sep)[-1],
        file_path=bedpe_file,
        windowsize=windowsize,
    )
    db.session.add(new_entry)
    db.session.commit()


def perform_pileup(cooler_dataset, intervals, binsize, arms, pileup_type):
    """Performs pileup [either ICCF or Obs/Exp; parameter passed to pileup_type] of cooler_dataset on
    intervals with resolution binsize."""
    log.info(
        f"  Doing pileup on cooler {cooler_dataset.id} with intervals {intervals.id} on binsize {binsize}"
    )
    # get path to dataset
    file_path = intervals.source_dataset.file_path
    # get windowsize
    window_size = intervals.windowsize
    # check whether windowsize is divisible by binsize
    if window_size % int(binsize) != 0:
        log.warn(
            "      ########### Windowsize and binsize do not match! ##############"
        )
        return
    # load bedfile
    log.info("      Loading regions...")
    regions = pd.read_csv(file_path, sep="\t", header=None)
    if len(regions.columns) > 2:
        # region definition with start and end
        regions = regions.rename(columns={0: "chrom", 1: "start", 2: "end"})
        regions.loc[:, "pos"] = (regions["start"] + regions["end"]) // 2
    else:
        # region definition with start
        regions = regions.rename(columns={0: "chrom", 1: "pos"})
    # do pileup
    log.info("      Doing pileup...")
    cooler_file = cooler.Cooler(cooler_dataset.file_path + f"::/resolutions/{binsize}")
    pileup_windows = HT.assign_regions(
        window_size, int(binsize), regions["chrom"], regions["pos"], arms
    ).dropna()
    if pileup_type == "Obs/Exp":
        expected = HT.get_expected(cooler_file, arms, proc=2)
        pileup_array = HT.do_pileup_obs_exp(
            cooler_file, expected, pileup_windows, proc=1
        )
    else:
        pileup_array = HT.do_pileup_iccf(cooler_file, pileup_windows, proc=1)
    # prepare dataframe for js reading1
    log.info("      Writing output...")
    file_name = uuid.uuid4().hex + ".npy"
    file_path = os.path.join(current_app.config["UPLOAD_DIR"], file_name)
    np.save(file_path, pileup_array)
    # add this to database
    log.info("      Adding database entry...")
    add_pileup_db(file_path, binsize, intervals.id, cooler_dataset.id, pileup_type)
    log.info("      Success!")


def perform_stackup(bigwig_dataset, intervals, binsize):
    """Performs stackup of bigwig dataset over the intervals provided with the indicated binsize.
    Stores result and adds it to database."""
    log.info(
        f"  Doing pileup on bigwig {bigwig_dataset.id} with intervals {intervals.id} on binsize {binsize}"
    )
    # get path to dataset
    file_path = intervals.source_dataset.file_path
    # get windowsize
    window_size = intervals.windowsize
    # load bedfile
    log.info("      Loading regions...")
    regions = pd.read_csv(file_path, sep="\t", header=None)
    if len(regions.columns) > 2:
        # region definition with start and end
        regions = regions.rename(columns={0: "chrom", 1: "start", 2: "end"})
        regions.loc[:, "pos"] = (regions["start"] + regions["end"]) // 2
    else:
        # region definition with start
        regions = regions.rename(columns={0: "chrom", 1: "pos"})
    # construct stackup-regions: positions - windowsize until position + windowsize
    stackup_regions = pd.DataFrame(
        {
            "chrom": regions["chrom"],
            "start": regions["pos"]
            - window_size,  # regions outside of chromosomes will be filled with NaN by pybbi
            "end": regions["pos"] + window_size,
        }
    )
    # calculate number of bins
    bin_number = int(window_size / binsize) * 2
    # make arget array
    target_array = np.empty((len(stackup_regions), bin_number))
    target_array.fill(np.nan)
    # filter stackup_regions for chromoosmes that are in bigwig
    chromosome_names = bbi.chromsizes(bigwig_dataset.file_path).keys()
    is_good_chromosome = [True if chrom in chromosome_names else False for chrom in stackup_regions["chrom"]]
    good_chromosome_indices = np.arange(len(stackup_regions))[is_good_chromosome]
    good_regions = stackup_regions.iloc[good_chromosome_indices, :]
    # extract data
    stackup_array = bbi.stackup(
        bigwig_dataset.file_path,
        chroms=good_regions["chrom"].to_list(),
        starts=good_regions["start"].to_list(),
        ends=good_regions["end"].to_list(),
        bins=bin_number,
        missing=np.nan,
    )
    # put extracted data back in target array
    target_array[good_chromosome_indices, :] = stackup_array
    # save full length array to file
    log.info("      Writing output...")
    file_uuid = uuid.uuid4().hex
    file_name = file_uuid + ".npy"
    file_name_line = file_uuid + "_line.npy"
    file_path = os.path.join(current_app.config["UPLOAD_DIR"], file_name)
    file_path_line = os.path.join(current_app.config["UPLOAD_DIR"], file_name_line)
    np.save(file_path, target_array)
    line_array = np.nanmean(target_array, axis=0)
    np.save(file_path_line, line_array)
    # save downsampled array to file
    if len(stackup_regions) < current_app.config["STACKUP_THRESHOLD"]:
        # if there are less than 1000 examples, small file is the same as large file
        file_path_small = file_path
        # store an index file
        indices = np.arange(len(stackup_regions))
        index_file = os.path.join(
            current_app.config["UPLOAD_DIR"], file_uuid + "_indices.npy"
        )
        np.save(index_file, indices)
    else:
        # set random seed
        np.random.seed(42)
        # subsample
        index = np.arange(len(stackup_regions))
        sub_sample_index = np.random.choice(
            index, current_app.config["STACKUP_THRESHOLD"]
        )
        downsampled_array = target_array[sub_sample_index, :]
        file_name_small = file_uuid + "_small.npy"
        file_path_small = os.path.join(
            current_app.config["UPLOAD_DIR"], file_name_small
        )
        # store file
        np.save(file_path_small, downsampled_array)
        # store indices
        index_file = os.path.join(
            current_app.config["UPLOAD_DIR"], file_uuid + "_indices.npy"
        )
        np.save(index_file, sub_sample_index)
    # add to database
    log.info("      Adding database entry...")
    add_stackup_db(
        file_path, file_path_small, index_file, binsize, intervals.id, bigwig_dataset.id
    )
    add_line_db(file_path_line, binsize, intervals.id, bigwig_dataset.id)
    log.info("      Success!")


def add_stackup_db(
    file_path, file_path_small, index_file, binsize, intervals_id, bigwig_dataset_id
):
    """Adds stackup to database"""
    # check if old individual interval data exists and delete them
    test_query = IndividualIntervalData.query.filter(
        (IndividualIntervalData.binsize
        == int(binsize)) & (IndividualIntervalData.intervals_id
        == intervals_id) & (IndividualIntervalData.dataset_id
        == bigwig_dataset_id)
    ).all()
    for entry in test_query:
        remove_safely(entry.file_path)
        remove_safely(entry.file_path_small)
        remove_safely(entry.file_path_indices_small)
        db.session.delete(entry)
    # add new entry
    new_entry = IndividualIntervalData(
        binsize=int(binsize),
        name=os.path.basename(file_path),
        file_path=file_path,
        file_path_small=file_path_small,
        file_path_indices_small=index_file,
        intervals_id=intervals_id,
        dataset_id=bigwig_dataset_id,
    )
    db.session.add(new_entry)
    db.session.commit()


def add_line_db(file_path, binsize, intervals_id, bigwig_dataset_id):
    """Adds pileup region to database"""
    # check if old average interval data exists and delete them
    test_query = AverageIntervalData.query.filter(
        (AverageIntervalData.binsize
        == int(binsize)) & (AverageIntervalData.intervals_id
        == intervals_id) & (AverageIntervalData.dataset_id
        == bigwig_dataset_id)
    ).all()
    for entry in test_query:
        remove_safely(entry.file_path)
        db.session.delete(entry)
    # add new entry
    new_entry = AverageIntervalData(
        binsize=int(binsize),
        name=os.path.basename(file_path),
        file_path=file_path,
        intervals_id=intervals_id,
        dataset_id=bigwig_dataset_id,
        value_type="line",
    )
    db.session.add(new_entry)
    db.session.commit()


def add_pileup_db(file_path, binsize, intervals_id, cooler_dataset_id, pileup_type):
    """Adds pileup region to database and deletes any old pileups with the same parameter combination."""
    # check if old average interval data exists and delete them
    test_query = AverageIntervalData.query.filter(
        (AverageIntervalData.binsize
        == int(binsize)) & (AverageIntervalData.intervals_id
        == intervals_id) & (AverageIntervalData.dataset_id
        == cooler_dataset_id) & (AverageIntervalData.value_type == pileup_type)
    ).all()
    for entry in test_query:
        remove_safely(entry.file_path)
        db.session.delete(entry)
    # add new entry
    new_entry = AverageIntervalData(
        binsize=int(binsize),
        name=os.path.basename(file_path),
        file_path=file_path,
        intervals_id=intervals_id,
        dataset_id=cooler_dataset_id,
        value_type=pileup_type,
    )
    db.session.add(new_entry)
    db.session.commit()


def _set_task_progress(progress):
    job = get_current_job()
    if job:
        job.meta["progress"] = progress
        job.save_meta()
        task = Task.query.get(job.get_id())
        if progress >= 100:
            task.complete = True
            db.session.commit()
