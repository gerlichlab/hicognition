"""Tasks for the redis-queue"""
import os
import logging


import pandas as pd
from hicognition import io_helpers
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
    for window in window_sizes:
        # preprocessing
        pipeline_steps.bed_preprocess_pipeline_step(dataset_id, window)
    pipeline_steps._set_task_progress(100)


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