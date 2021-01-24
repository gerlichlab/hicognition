"""Pipeline steps for redis queue"""
import os
import uuid
import logging

from flask.globals import current_app
import pandas as pd
import numpy as np
from ngs import HiCTools as HT
import cooler
from hicognition import higlass_interface
import bbi
from requests.exceptions import HTTPError
from rq import get_current_job
from . import db
from .models import Dataset, Intervals, AverageIntervalData, Task, IndividualIntervalData

# get logger
log = logging.getLogger("rq.worker")


def bed_preprocess_pipeline_step(dataset_id):
    """Runs bed-preprocess pipeline step of pipeline_bed:
    - run clodius on bedfile
    - upload clodius result to higlass
    - store higlass_uuid in Dataset db entry
    """
    log.info(f"  Running bed-preprocessing for ID {dataset_id}")
    # get dataset, this is not sorted, not preprocessed for higlass
    current_dataset = Dataset.query.get(dataset_id)
    # preprocess with clodius
    log.info("Clodius preprocessing...")
    dataset_file = current_dataset.file_path
    output_path = dataset_file + ".beddb"
    exit_code = higlass_interface.preprocess_dataset(
        "bedfile", current_app.config["CHROM_SIZES"], dataset_file, output_path
    )
    if exit_code != 0:
        log.error("Clodius failed!")
        raise ValueError("Clodius failed!")
    # add to higlass
    log.info("      Add to higlass...")
    credentials = {
        "user": current_app.config["HIGLASS_USER"],
        "password": current_app.config["HIGLASS_PWD"],
    }
    try:
        result = higlass_interface.add_tileset(
            "bedfile",
            output_path,
            current_app.config["HIGLASS_API"],
            credentials,
            current_dataset.dataset_name,
        )
    except HTTPError:
        log.error("Higlass upload of bedfile failed")
        return
    # upload succeeded, add uuid
    uuid = result["uuid"]
    current_dataset.higlass_uuid = uuid
    db.session.commit()
    log.info("      Success!")


def bedpe_preprocess_pipeline_step(file_path, dataset_id=None, windowsize=None):
    """
    Performs bedpe preprocessing pipeline step:
    * run clodius on bedpe file
    * upload result to higlass
    * add Intervals dataset entry
    """
    log.info(f"  Bedpe-preprocess: {file_path} with {windowsize}")
    # run clodius
    log.info(f"     Running clodius...")
    clodius_output = file_path + ".bed2ddb"
    exit_code = higlass_interface.preprocess_dataset(
        "bedpe", current_app.config["CHROM_SIZES"], file_path, clodius_output
    )
    if exit_code != 0:
        log.error("Clodius failed!")
        raise ValueError("Clodius failed!")
    # add to higlass
    log.info("      Adding to higlass...")
    credentials = {
        "user": current_app.config["HIGLASS_USER"],
        "password": current_app.config["HIGLASS_PWD"],
    }
    dataset_name = clodius_output.split("/")[-1]
    try:
        result = higlass_interface.add_tileset(
            "bedpe",
            clodius_output,
            current_app.config["HIGLASS_API"],
            credentials,
            dataset_name,
        )
    except HTTPError:
        log.error("Higlass upload failed!")
        return
    # upload succeeded, add things to database
    uuid = result["uuid"]
    new_entry = Intervals(
        dataset_id=dataset_id,
        name=dataset_name,
        file_path=clodius_output,
        higlass_uuid=uuid,
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
    file_name = uuid.uuid4().hex + ".csv"
    file_path = os.path.join(current_app.config["UPLOAD_DIR"], file_name)
    export_df_for_js(pileup_array, file_path)
    # add this to database
    log.info("      Adding database entry...")
    add_pileup_db(file_path, binsize, intervals.id, cooler_dataset.id, pileup_type)
    log.info("      Success!")


def perform_stackup(bigwig_dataset, intervals, binsize):
    """Performs stackup of bigwig dataset over the intervals provided with the indicated binsize.
    Stores result and adds it to database."""
    log.info(
        f"  Doing pileup on cooler {bigwig_dataset.id} with intervals {intervals.id} on binsize {binsize}"
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
            "start": regions["pos"] - window_size, # regions outside of chromosomes will be filled with NaN by pybbi
            "end": regions["end"] + window_size,
        }
    )
    # calculate number of bins
    bin_number = int(window_size / binsize) * 2
    # extract data
    stackup_array = bbi.stackup(
        bigwig_dataset.file_path,
        chroms=stackup_regions["chroms"],
        starts=stackup_regions["starts"],
        ends=stackup_regions["ends"],
        bins=bin_number,
        missing=np.nan
    )
    # save full length array to file
    log.info("      Writing output...")
    file_name = uuid.uuid4().hex + ".npy"
    file_path = os.path.join(current_app.config["UPLOAD_DIR"], file_name)
    np.save(file_path, stackup_array)
    # save downsampled array to file
    if stackup_array.shape[0] < 1000:
        # if there are less than 1000 examples, small file is the same as large file
        file_path_small = file_path
    else:
        # set random seed
        np.random.seed(42)
        # subsmple
        index = np.arange(stackup_array.shape[0])
        sub_sample_index = np.random.choice(index, 1000)
        downsampled_array = stackup_array[sub_sample_index, :]
        file_name_small = uuid.uuid4().hex + ".npy"
        file_path_small = os.path.join(current_app.config["UPLOAD_DIR"], file_name_small)
        np.save(file_path_small, downsampled_array)
    # add to database
    log.info("      Adding database entry...")
    add_stackup_db(file_path, file_path_small, binsize, intervals.id, bigwig_dataset.id)
    log.info("      Success!")


def export_df_for_js(np_array, file_path):
    """exports a pileup dataframe
    so it can be easily read and used by
    d3.js"""
    output_molten = (
        pd.DataFrame(np_array)
        .stack()
        .reset_index()
        .rename(columns={"level_0": "variable", "level_1": "group", 0: "value"})
    )
    # write to file
    output_molten.to_csv(file_path, index=False)


def add_stackup_db(file_path, file_path_small ,binsize, intervals_id, bigwig_dataset_id):
    """Adds stackup to database"""
    new_entry = IndividualIntervalData(
        binsize=int(binsize),
        name=os.path.basename(file_path),
        file_path=file_path,
        file_path_small=file_path_small,
        intervals_id=intervals_id,
        dataset_id=bigwig_dataset_id
    )
    db.session.add(new_entry)
    db.session.commit()

def add_pileup_db(file_path, binsize, intervals_id, cooler_dataset_id, pileup_type):
    """Adds pileup region to database"""
    new_entry = AverageIntervalData(
        binsize=int(binsize),
        name=os.path.basename(file_path),
        file_path=file_path,
        intervals_id=intervals_id,
        cooler_id=cooler_dataset_id,
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
