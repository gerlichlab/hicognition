"""Tasks for the redis-queue"""
import os
import logging


import pandas as pd
from hicognition import io_helpers, higlass_interface
from requests.exceptions import HTTPError
from . import create_app, db
from .models import Dataset, Intervals
from . import pipeline_steps

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
        * Add Intervals dataset entry
    - Indicate in Job table in database that job is complete.
    Output-folder is not needed for this since the file_path
    of Dataset entry contains it.
    """
    window_sizes = app.config["WINDOW_SIZES"]
    log.info(f"Bed pipeline started for {dataset_id} with {window_sizes}")
    # bed-file preprocessing: sorting, clodius, uploading to higlass
    file_path = Dataset.query.get(dataset_id).file_path
    # sort dataset
    log.info("      Sorting...")
    sorted_file_name = file_path.split(".")[0] + "_sorted.bed"
    io_helpers.sort_bed(file_path, sorted_file_name, app.config["CHROM_SIZES"])
    # set sorted_file_name as file_name
    dataset_object = Dataset.query.get(dataset_id)
    dataset_object.file_path = sorted_file_name
    db.session.commit()
    pipeline_steps.bed_preprocess_pipeline_step(dataset_id)
    pipeline_steps._set_task_progress(50)
    for window in window_sizes:
        # Convert to bedpe
        log.info(f"  Converting to bedpe, windowsize {window}")
        target_file = sorted_file_name + f".{window}" + ".bedpe"
        io_helpers.convert_bed_to_bedpe(sorted_file_name, target_file, window)
        # preprocessing
        pipeline_steps.bedpe_preprocess_pipeline_step(target_file, dataset_id, window)
    pipeline_steps._set_task_progress(100)


def pipeline_cooler(dataset_id):
    """Starts the pipeline for
    cooler-files. Pipeline:
    - Add to higlass and update uuid
    - Indicate in Job table in database that job is complete
    - Set dataset status to "uploaded"
    """
    log.info(f"Cooler pipeline started for {dataset_id}")
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
        log.error(f"Higlass upload of cooler with it {dataset_id} failed")
        return
    # upload succeeded, add uuid of higlass to dataset
    uuid = result["uuid"]
    current_dataset.higlass_uuid = uuid
    db.session.commit()

def pipeline_bigwig(dataset_id):
    """Starts the pipeline for
    bigwig-files. Pipeline:
    - Add to higlass and update uuid
    - Indicate in Job table in database that job is complete
    - Set dataset status to "uploaded"
    """
    log.info(f"Bigwig pipeline started for {dataset_id}")
    current_dataset = Dataset.query.get(dataset_id)
    # upload to higlass
    log.info("  Uploading to higlass...")
    credentials = {
        "user": app.config["HIGLASS_USER"],
        "password": app.config["HIGLASS_PWD"],
    }
    try:
        result = higlass_interface.add_tileset(
            "bigwig",
            current_dataset.file_path,
            app.config["HIGLASS_API"],
            credentials,
            current_dataset.dataset_name,
        )
    except HTTPError:
        log.error("Higlass upload of bigwig failed")
        return
    # upload succeeded, add uuid of higlass to dataset
    uuid = result["uuid"]
    current_dataset.higlass_uuid = uuid
    db.session.commit()


def pipeline_pileup(dataset_id, binsizes, interval_ids):
    """Start pileup pipeline for specified combination of
    dataset_id (cooler_file), binsizes and intervals"""
    current_dataset = Dataset.query.get(dataset_id)
    interval_datasets = Intervals.query.filter(Intervals.id.in_(interval_ids)).all()
    chromosome_arms = pd.read_csv(app.config["CHROM_ARMS"])
    # perform pileup
    counter = 0
    for binsize in binsizes:
        for intervals in interval_datasets:
            pipeline_steps.perform_pileup(current_dataset, intervals, binsize, chromosome_arms, "ICCF")
            pipeline_steps.perform_pileup(current_dataset, intervals, binsize, chromosome_arms, "Obs/Exp")
            counter += 1
            progress = counter / (len(binsizes) * len(interval_datasets)) * 100
            pipeline_steps._set_task_progress(progress)
    pipeline_steps._set_task_progress(100)


def pipeline_stackup(dataset_id, binsizes, interval_ids):
    """Start stackup pipeline for specified combination of
    dataset_id (bigwig file), binsizes and intervals"""
    current_dataset = Dataset.query.get(dataset_id)
    interval_datasets = Intervals.query.filter(Intervals.id.in_(interval_ids)).all()
    # perform stackup
    counter = 0
    for binsize in binsizes:
        for intervals in interval_datasets:
            pipeline_steps.perform_stackup(current_dataset, intervals, binsize)
            counter += 1
            progress = counter / (len(binsizes) * len(interval_datasets)) * 100
            pipeline_steps._set_task_progress(progress)
    pipeline_steps._set_task_progress(100)