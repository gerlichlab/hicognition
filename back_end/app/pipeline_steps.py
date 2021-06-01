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
    # generate subsample index for smaller stackup
    bedpe = pd.read_csv(bedpe_file, sep="\t", header=None)
    index_file = os.path.join(
            current_app.config["UPLOAD_DIR"], bedpe_file.split(os.sep)[-1] + "_indices.npy"
        )
    if len(bedpe) < current_app.config["STACKUP_THRESHOLD"]:
        # if there are less rows than the stackup theshold, index file are the indices of this file
        sub_sample_index = np.arange(len(bedpe))
    else:
        # set random seed
        np.random.seed(42)
        # subsample
        all_indices = np.arange(len(bedpe))
        sub_sample_index = np.random.choice(
            all_indices, current_app.config["STACKUP_THRESHOLD"]
        )
    # store indices
    np.save(index_file, sub_sample_index)
    # Commit to database
    new_entry = Intervals(
        dataset_id=dataset_id,
        name=bedpe_file.split(os.sep)[-1],
        file_path=bedpe_file,
        file_path_sub_sample_index=index_file,
        windowsize=windowsize,
    )
    db.session.add(new_entry)
    db.session.commit()


def perform_pileup(cooler_dataset_id, interval_id, binsize, arms, pileup_type):
    """Performs pileup [either ICCF or Obs/Exp; parameter passed to pileup_type] of cooler_dataset on
    intervals with resolution binsize."""
    log.info(
        f"  Doing pileup on cooler {cooler_dataset_id} with intervals { interval_id} on binsize {binsize}"
    )
    cooler_dataset = Dataset.query.get(cooler_dataset_id)
    intervals = Intervals.query.get(interval_id)
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
        expected = HT.get_expected(cooler_file, arms, proc=current_app.config["OBS_EXP_PROCESSES"])
        pileup_array = HT.do_pileup_obs_exp(
            cooler_file, expected, pileup_windows, proc=current_app.config["PILEUP_PROCESSES"]
        )
    else:
        pileup_array = HT.do_pileup_iccf(cooler_file, pileup_windows, proc=current_app.config["PILEUP_PROCESSES"])
    # prepare dataframe for js reading1
    log.info("      Writing output...")
    file_name = uuid.uuid4().hex + ".npy"
    file_path = os.path.join(current_app.config["UPLOAD_DIR"], file_name)
    np.save(file_path, pileup_array)
    # add this to database
    log.info("      Adding database entry...")
    add_pileup_db(file_path, binsize, intervals.id, cooler_dataset.id, pileup_type)
    log.info("      Success!")


def perform_stackup(bigwig_dataset_id, intervals_id, binsize):
    """Performs stackup of bigwig dataset over the intervals provided with the indicated binsize.
    Stores result and adds it to database."""
    log.info(
        f"  Doing pileup on bigwig {bigwig_dataset_id} with intervals {intervals_id} on binsize {binsize}"
    )
    bigwig_dataset = Dataset.query.get(bigwig_dataset_id)
    intervals = Intervals.query.get(intervals_id)
    # get path to dataset
    file_path = intervals.source_dataset.file_path
    # get windowsize
    window_size = intervals.windowsize
    # load bedfile
    log.info("      Loading regions...")
    regions = pd.read_csv(file_path, sep="\t", header=None)
    sub_sample_index = np.load(intervals.file_path_sub_sample_index)
    regions_small = regions.iloc[sub_sample_index, :]
    log.info("      Doing stackup...")
    full_size_array = _do_stackup(regions, window_size, binsize, bigwig_dataset.file_path)
    downsampled_array = _do_stackup(regions_small, window_size, binsize, bigwig_dataset.file_path)
    # save full length array to file
    log.info("      Writing output...")
    file_uuid = uuid.uuid4().hex
    file_name = file_uuid + ".npy"
    file_name_line = file_uuid + "_line.npy"
    file_path = os.path.join(current_app.config["UPLOAD_DIR"], file_name)
    file_path_line = os.path.join(current_app.config["UPLOAD_DIR"], file_name_line)
    np.save(file_path, full_size_array)
    line_array = np.nanmean(full_size_array, axis=0)
    np.save(file_path_line, line_array)
    # save small array to file
    file_name_small = file_uuid + "_small.npy"
    file_path_small = os.path.join(
        current_app.config["UPLOAD_DIR"], file_name_small
    )
    np.save(file_path_small, downsampled_array)
    # add to database
    log.info("      Adding database entry...")
    add_stackup_db(
        file_path, file_path_small, binsize, intervals.id, bigwig_dataset.id
    )
    add_line_db(file_path_line, binsize, intervals.id, bigwig_dataset.id)
    log.info("      Success!")


def add_stackup_db(
    file_path, file_path_small, binsize, intervals_id, bigwig_dataset_id
):
    """Adds stackup to database"""
    # check if old individual interval data exists and delete them
    test_query = IndividualIntervalData.query.filter(
        (IndividualIntervalData.binsize == int(binsize))
        & (IndividualIntervalData.intervals_id == intervals_id)
        & (IndividualIntervalData.dataset_id == bigwig_dataset_id)
    ).all()
    for entry in test_query:
        remove_safely(entry.file_path)
        remove_safely(entry.file_path_small)
        db.session.delete(entry)
    # add new entry
    new_entry = IndividualIntervalData(
        binsize=int(binsize),
        name=os.path.basename(file_path),
        file_path=file_path,
        file_path_small=file_path_small,
        intervals_id=intervals_id,
        dataset_id=bigwig_dataset_id,
    )
    db.session.add(new_entry)
    db.session.commit()


def add_line_db(file_path, binsize, intervals_id, bigwig_dataset_id):
    """Adds pileup region to database"""
    # check if old average interval data exists and delete them
    test_query = AverageIntervalData.query.filter(
        (AverageIntervalData.binsize == int(binsize))
        & (AverageIntervalData.intervals_id == intervals_id)
        & (AverageIntervalData.dataset_id == bigwig_dataset_id)
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
        (AverageIntervalData.binsize == int(binsize))
        & (AverageIntervalData.intervals_id == intervals_id)
        & (AverageIntervalData.dataset_id == cooler_dataset_id)
        & (AverageIntervalData.value_type == pileup_type)
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


def _do_stackup(regions, window_size, binsize, bigwig_dataset):
    """Takes a set of regions, window_size, binsize as well as the path to a bigwig file and
    extracts data along those regions."""
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
    chromosome_names = bbi.chromsizes(bigwig_dataset).keys()
    is_good_chromosome = [
        True if chrom in chromosome_names else False
        for chrom in stackup_regions["chrom"]
    ]
    good_chromosome_indices = np.arange(len(stackup_regions))[is_good_chromosome]
    good_regions = stackup_regions.iloc[good_chromosome_indices, :]
    # extract data
    stackup_array = bbi.stackup(
        bigwig_dataset,
        chroms=good_regions["chrom"].to_list(),
        starts=good_regions["start"].to_list(),
        ends=good_regions["end"].to_list(),
        bins=bin_number,
        missing=np.nan,
    )
    # put extracted data back in target array
    target_array[good_chromosome_indices, :] = stackup_array
    return target_array

def _set_task_progress(progress):
    job = get_current_job()
    if job:
        job.meta["progress"] = progress
        job.save_meta()
        task = Task.query.get(job.get_id())
        if progress >= 100:
            task.complete = True
            db.session.commit()
