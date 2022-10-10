"""Tasks for the redis-queue"""
import os
import logging
from flask import current_app
import pandas as pd
from datetime import datetime
from requests.exceptions import ConnectionError, Timeout
from hicognition import io_helpers
from rq import get_current_job
from . import create_app, db
from .models import (
    Assembly,
    Dataset,
    IndividualIntervalData,
    Collection,
)
from . import pipeline_steps
from .notifications import NotificationHandler

# from .file_utils import download_ENCODE_metadata, download_file
from . import download_utils

# get logger
log = logging.getLogger("rq.worker")

app = None
# setup app context
# def task_context(func):
#     def create_context():
#         app = create_app(os.getenv("FLASK_CONFIG") or "default")
#         app.app_context().push()
#     return create_context
app = create_app(os.getenv("FLASK_CONFIG") or "default")
app.app_context().push()

# set up notification handler

notification_handler = NotificationHandler()

# set basedir

basedir = os.path.abspath(os.path.dirname(__file__))  # TODO unused

# # @task_context
def pipeline_bed(dataset_id):
    """Starts the pipeline for
    bed-files. Pipeline:
    - sort bedfile associated with dataset_id
    - Indicate in Job table in database that job is complete.
    Output-folder is not needed for this since the file_path
    of Dataset entry contains it.
    """
    dataset_object = Dataset.query.get(dataset_id)
    if dataset_object.sizeType == "Interval":
        window_sizes = ["variable"]
    else:
        window_sizes = [
            size
            for size in app.config["PREPROCESSING_MAP"].keys()
            if size != "variable"
        ]
    log.info(f"Bed pipeline started for {dataset_id} with {window_sizes}")
    # bed-file preprocessing: sorting, clodius, uploading to higlass
    file_path = dataset_object.file_path
    # clean dataset
    log.info("      Clean...")
    cleaned_file_name = file_path.split(".")[0] + "_cleaned.bed"
    io_helpers.clean_bed(file_path, cleaned_file_name)
    # set cleaned_file_name as file_name
    dataset_object.file_path = cleaned_file_name
    # delete old file
    log.info("      Delete Unsorted...")
    io_helpers.remove_safely(file_path, current_app.logger)
    db.session.commit()
    for window in window_sizes:
        # preprocessing
        pipeline_steps.bed_preprocess_pipeline_step(dataset_id, window)
    pipeline_steps.set_task_progress(100)


# @task_context
def pipeline_pileup(dataset_id, intervals_id, binsize):
    """Start pileup pipeline for specified combination of
    dataset_id (cooler_file), binsize and intervals_id"""
    try:
        chromosome_arms = pd.read_csv(
            Assembly.query.get(Dataset.query.get(dataset_id).assembly).chrom_arms
        )
        pipeline_steps.pileup_pipeline_step(
            dataset_id, intervals_id, binsize, chromosome_arms, "ICCF"
        )
        pipeline_steps.pileup_pipeline_step(
            dataset_id, intervals_id, binsize, chromosome_arms, "Obs/Exp"
        )
        pipeline_steps.set_task_progress(100)
        pipeline_steps.set_dataset_finished(dataset_id, intervals_id)
    except BaseException as err:
        pipeline_steps.set_dataset_failed(dataset_id, intervals_id)
        log.error(err, exc_info=True)


# @task_context
def pipeline_stackup(dataset_id, intervals_id, binsize):
    """Start stackup pipeline for specified combination of
    dataset_id (bigwig file), binsize and intervals_id"""
    try:
        pipeline_steps.stackup_pipeline_step(dataset_id, intervals_id, binsize)
        pipeline_steps.set_task_progress(100)
        pipeline_steps.set_dataset_finished(dataset_id, intervals_id)
    except BaseException as err:
        pipeline_steps.set_dataset_failed(dataset_id, intervals_id)
        log.error(err, exc_info=True)


# @task_context
def pipeline_lola(collection_id, intervals_id, binsize):
    """Starts lola enrichment calculation pipeline step for a specific
    collection_id, binsize and intervals_id"""
    try:
        pipeline_steps.enrichment_pipeline_step(collection_id, intervals_id, binsize)
        pipeline_steps.set_task_progress(100)
        pipeline_steps.set_collection_finished(collection_id, intervals_id)
    except BaseException as err:
        pipeline_steps.set_collection_failed(collection_id, intervals_id)
        log.error(err, exc_info=True)


# @task_context
def pipeline_embedding_1d(collection_id, intervals_id, binsize):
    """Starts embedding pipeline steps for feature collections refering to
    1-dimensional features per regions (e.g. bigwig tracks)"""
    # check whether stackups exist and perform stackup if not
    try:
        for source_dataset in Collection.query.get(collection_id).datasets:
            stackup = IndividualIntervalData.query.filter(
                (IndividualIntervalData.dataset_id == source_dataset.id)
                & (IndividualIntervalData.intervals_id == intervals_id)
                & (IndividualIntervalData.binsize == binsize)
            ).first()
            if stackup is None:
                pipeline_steps.stackup_pipeline_step(
                    source_dataset.id, intervals_id, binsize
                )
        # perform embedding
        pipeline_steps.embedding_1d_pipeline_step(collection_id, intervals_id, binsize)
        pipeline_steps.set_task_progress(100)
        pipeline_steps.set_collection_finished(collection_id, intervals_id)
    except BaseException as err:
        pipeline_steps.set_collection_failed(collection_id, intervals_id)
        log.error(err, exc_info=True)


# @task_context
def download_dataset_file(dataset_id: int):
    """
    Downloads dataset file from web and validates + 'preprocesses' it.
    ua
    - ua: have put this in tasks, as this made most sense.
    - ua: I would actually put this into download_functions.py if possible.

    """

    def handle_error(ds: Dataset, msg: str):
        send_notification(ds, f"Dataset creation failed:<br>{msg}", "failed")
        pipeline_steps.set_task_progress(100)

        db.session.delete(ds)
        db.session.commit()

    def send_notification(ds: Dataset, msg: str, status: str = "success"):
        notification_handler.send_notification_general(
            {
                "id": -1 if get_current_job() is None else get_current_job().get_id(),
                "dataset_name": ds.dataset_name,
                "time": datetime.now(),
                "notification_type": "upload_notification",
                "owner": ds.user.id,
                "message": msg,
                "status": status,
            }
        )

    dataset = Dataset.query.get(dataset_id)
    if not dataset:
        log.info(f"Dataset {dataset_id} not found")
        handle_error(dataset, f"Dataset with id {dataset.id} was not found.")
        return

    # check whether either url or sample id are provided:
    if not (dataset.sample_id and dataset.repository_name) and not dataset.source_url:
        log.info(f"No sample_id, repo_name or source_url provided for {dataset.id}")
        handle_error(
            dataset, f"Neither sample id + repository, nor file URL have been provided."
        )
        return

    is_repository = dataset.sample_id and dataset.repository
    try:
        if is_repository:
            download_utils.download_encode(dataset, current_app.config["UPLOAD_DIR"])
        else:
            download_utils.download_url(
                dataset,
                current_app.config["UPLOAD_DIR"],
                current_app.config["DATASET_OPTION_MAPPING"]["supported_file_endings"][
                    dataset.filetype
                ][0],
            )
    except (ConnectionError, Timeout) as err:
        log.info(f"Connection failure: {str(err)}")
        handle_error(
            dataset, f"Connection to external server failed at some point: {str(err)}"
        )
    except download_utils.DownloadUtilsException as err:
        log.info(str(err))
        handle_error(dataset, str(err))
        return

    db.session.commit()

    valid = dataset.validate_dataset(delete=True)
    if not valid:
        log.info(f"Dataset {dataset.id} file was invalid.")
        handle_error(dataset, "File formatting was invalid.")
        return

    dataset.preprocess_dataset()
    db.session.commit()
    send_notification(
        dataset, "Dataset file download was successful!<br>Ready for preprocessing."
    )  # TODO preprocessing ambiguous
    log.info("Success.")
    pipeline_steps.set_task_progress(100)
