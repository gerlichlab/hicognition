"""Tasks for the redis-queue"""
import os
import uuid
import logging

from flask.globals import current_app
import pandas as pd
from ngs import HiCTools as HT
import cooler
from hicognition import io_helpers, higlass_interface
from requests.exceptions import HTTPError
from rq import get_current_job
from . import create_app, db
from .models import Dataset, Pileupregion, Pileup, Task

# get logger
log = logging.getLogger("rq.worker")

# setup app context

app = create_app(os.getenv("FLASK_CONFIG") or "default")
app.app_context().push()

# set basedir

basedir = os.path.abspath(os.path.dirname(__file__))


def pipeline_bed(dataset_id):
    """Starts the pipeline for
    bed-files. Pipeline:
    - sort bedfile associated with dataset_id
    - run clodius on sorted bedfile
    - upload clodius result to higlass
    - store higlass_uuid in Dataset db entry
    - For each windowsize in window_sizes, do:
        * convert bed to bedpe
        * run clodius on bedpe
        * upload result to higlass
        * Add PileupRegion dataset entry
    - Indicate in Job table in database that job is complete.
    Output-folder is not needed for this since the file_path
    of Dataset entry contains it.
    """
    window_sizes = app.config["WINDOW_SIZES"]
    log.info(f"Bed pipeline started for {dataset_id} with {window_sizes}")
    # bed-file preprocessing: sorting, clodius, uploading to higlass
    bed_preprocess_pipeline_step(dataset_id)
    _set_task_progress(50)
    file_path = Dataset.query.get(dataset_id).file_path
    # sort dataset
    log.info("      Sorting...")
    sorted_file_name = file_path.split(".")[0] + "_sorted.bed"
    io_helpers.sort_bed(file_path, sorted_file_name, app.config["CHROM_SIZES"])
    for window in window_sizes:
        # Convert to bedpe
        log.info(f"  Converting to bedpe, windowsize {window}")
        target_file = sorted_file_name + f".{window}" + ".bedpe"
        io_helpers.convert_bed_to_bedpe(sorted_file_name, target_file, window)
        # preprocessing
        bedpe_preprocess_pipeline_step(target_file, dataset_id, window)
    _set_task_progress(100)


def pipeline_cooler(dataset_id):
    """Starts the pipeline for
    cooler-files. Pipeline:
    - Add to higlass and update uuid
    - Indicate in Job table in database that job is complete
    - Set dataset status to "uploaded" # TODO
    """
    binsizes = app.config["BIN_SIZES"]
    log.info(f"Cooler pipeline started for {dataset_id} with {binsizes}")
    current_dataset = Dataset.query.get(dataset_id)
    # upload to higlass
    log.info("  Uploading to higlass...")
    credentials = {
        "user": app.config["HIGLASS_USER"],
        "password": app.config["HIGLASS_PWD"],
    }
    try:
        result = higlass_interface.add_tileset(
            "cooler",
            current_dataset.file_path,
            app.config["HIGLASS_API"],
            credentials,
            current_dataset.dataset_name,
        )
    except HTTPError:
        log.error("Higlass upload of bedfile failed")
        return
    # upload succeeded, add uuid of higlass to dataset
    uuid = result["uuid"]
    current_dataset.higlass_uuid = uuid
    db.session.commit()


def pipeline_pileup(dataset_id, binsizes, pileup_region_ids):
    """Start pileup pipeline for specified combination of
    cooler_id, binsizes and pileupregions"""
    current_dataset = Dataset.query.get(dataset_id)
    pileup_regions = Pileupregion.query.filter(Pileupregion.id.in_(pileup_region_ids)).all()
    chromosome_arms = pd.read_csv(app.config["CHROM_ARMS"])
    # perform pileup
    counter = 0
    for binsize in binsizes:
        for pileup_region in pileup_regions:
            perform_pileup(current_dataset, pileup_region, binsize, chromosome_arms, "ICCF")
            perform_pileup(current_dataset, pileup_region, binsize, chromosome_arms, "Obs/Exp")
            counter += 1
            progress = counter / (len(binsizes) * len(pileup_regions)) * 100
            _set_task_progress(progress)
    _set_task_progress(100)

# helpers


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
        "bedfile", app.config["CHROM_SIZES"], dataset_file, output_path
    )
    if exit_code != 0:
        log.error("Clodius failed!")
        raise ValueError("Clodius failed!")
    # add to higlass
    log.info("      Add to higlass...")
    credentials = {
        "user": app.config["HIGLASS_USER"],
        "password": app.config["HIGLASS_PWD"],
    }
    try:
        result = higlass_interface.add_tileset(
            "bedfile",
            output_path,
            app.config["HIGLASS_API"],
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
    * add Pileupregion dataset entry
    """
    log.info(f"  Bedpe-preprocess: {file_path} with {windowsize}")
    # run clodius
    log.info(f"     Running clodius...")
    clodius_output = file_path + ".bed2ddb"
    higlass_interface.preprocess_dataset(
        "bedpe", app.config["CHROM_SIZES"], file_path, clodius_output
    )
    # add to higlass
    log.info("      Adding to higlass...")
    credentials = {
        "user": app.config["HIGLASS_USER"],
        "password": app.config["HIGLASS_PWD"],
    }
    dataset_name = clodius_output.split("/")[-1]
    try:
        result = higlass_interface.add_tileset(
            "bedpe",
            clodius_output,
            app.config["HIGLASS_API"],
            credentials,
            dataset_name,
        )
    except HTTPError:
        log.error("Higlass upload failed!")
        return
    # upload succeeded, add things to database
    uuid = result["uuid"]
    new_entry = Pileupregion(
        dataset_id=dataset_id,
        name=dataset_name,
        file_path=clodius_output,
        higlass_uuid=uuid,
        windowsize=windowsize,
    )
    db.session.add(new_entry)
    db.session.commit()


def perform_pileup(cooler_dataset, pileup_region, binsize, arms, pileup_type):
    """Performs pileup [either ICCF or Obs/Exp; parameter passed to pileup_type] of cooler_dataset on
    pileup_region with resolution binsize."""
    log.info(
        f"  Doing pileup on cooler {cooler_dataset.id} with pileupregion {pileup_region.id} on binsize {binsize}"
    )
    # get path to dataset
    file_path = pileup_region.source_dataset.file_path
    # get windowsize
    window_size = pileup_region.windowsize
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
    pileup_windows = HT.assign_regions(window_size, int(binsize), regions["chrom"], regions["pos"], arms).dropna()
    if pileup_type == "Obs/Exp":
        expected = HT.get_expected(cooler_file, arms, proc=2)
        pileup_array = HT.do_pileup_obs_exp(cooler_file, expected, pileup_windows, proc=1)
    else:
        pileup_array = HT.do_pileup_iccf(cooler_file, pileup_windows, proc=1)
    # prepare dataframe for js reading1
    log.info("      Writing output...")
    file_name = uuid.uuid4().hex + ".csv"
    file_path = os.path.join(current_app.config["UPLOAD_DIR"], file_name)
    export_df_for_js(pileup_array, file_path)
    # add this to database
    log.info("      Adding database entry...")
    add_pileup_db(file_path, binsize, pileup_region.id, cooler_dataset.id, pileup_type)
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


def add_pileup_db(file_path, binsize, pileup_region_id, cooler_dataset_id, pileup_type):
    """Adds pileup region to database"""
    new_entry = Pileup(
        binsize=int(binsize),
        name=os.path.basename(file_path),
        file_path=file_path,
        pileupregion_id=pileup_region_id,
        cooler_id=cooler_dataset_id,
        value_type=pileup_type
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
