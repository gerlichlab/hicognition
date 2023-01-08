"""Tasks for the redis-queue"""
import os
import logging
from typing import Any
from datetime import datetime
from flask import current_app
import pandas as pd
from requests.exceptions import ConnectionError, Timeout
from .lib import io_helpers
from rq import get_current_job
from . import db
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


# set up notification handler

notification_handler = NotificationHandler()

# set basedir

basedir = os.path.abspath(os.path.dirname(__file__))  # TODO unused

# class WrongDatasetTypeError(Exception):
#     """Thrown if task is called with wrong dataset type"""

# hacked way to access functions by string as seen here:
# https://stackoverflow.com/questions/2447353/getattr-on-a-module
def __getattr__(name: str) -> Any:
    attr_dict = {
        "pipeline_bed": pipeline_bed,
        "pipeline_pileup": pipeline_pileup,
        "pipeline_stackup": pipeline_stackup,
        "pipeline_lola": pipeline_lola,
        "pipeline_embedding_1d": pipeline_embedding_1d,
        "download_dataset_file": download_dataset_file,
    }
    if name not in attr_dict:
        raise AttributeError(f"function {name} not in app.tasks")
    return attr_dict[name]


# # @task_context
def pipeline_bed(dataset_id):
    """Starts the pipeline for
    bed-files. Pipeline:
    - sort bedfile associated with dataset_id
    - Indicate in Job table in database that job is complete.
    Output-folder is not needed for this since the file_path
    of Dataset entry contains it.
    """
    dataset = Dataset.query.get(dataset_id)
    if dataset.sizeType == "Interval":
        window_sizes = ["variable"]
    else:
        window_sizes = [
            size
            for size in current_app.config["PREPROCESSING_MAP"].keys()
            if size != "variable"
        ]
    current_app.logger.info(f"Bed pipeline started for {dataset_id} with {window_sizes}")
    # bed-file preprocessing: sorting, clodius, uploading to higlass
    file_path = dataset.file_path
    # clean dataset
    current_app.logger.debug("      Clean...")
    dir_path = os.path.dirname(dataset.file_path)
    file_name_split = os.path.basename(dataset.file_path).split(".")
    file_name_cleaned = (
        f"{'.'.join(file_name_split[:-1])}_cleaned.{file_name_split[-1]}"
    )
    file_path_cleaned = os.path.join(dir_path, file_name_cleaned)

    if dataset.file_path.lower().endswith('bed'):
        io_helpers.clean_bed(file_path, file_path_cleaned)
    elif dataset.file_path.lower().endswith('bedpe'):
        io_helpers.clean_bedpe(file_path, file_path_cleaned)
    # set cleaned_file_name as file_name
    dataset.file_path = file_path_cleaned
    # delete old file
    current_app.logger.debug("      Delete Unsorted...")
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
        current_app.logger.error(err, exc_info=True)


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
        current_app.logger.error(err, exc_info=True)


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
        current_app.logger.error(err, exc_info=True)


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
        current_app.logger.error(err, exc_info=True)


def download_dataset_file(dataset_id: int):
    """
    Downloads dataset file from web and validates + 'preprocesses' it.
    """

    dataset = Dataset.query.get(dataset_id)
    if not dataset:
        current_app.logger.info(f"Dataset {dataset_id} not found")
        _handle_error(dataset, f"Dataset with id {dataset_id} was not found.")
        return

    # check whether either url or sample id are provided:
    if not ((dataset.sample_id and dataset.repository_name) or dataset.source_url):
        current_app.logger.info(f"No sample_id, repo_name or source_url provided for {dataset_id}")
        _handle_error(
            dataset,
            f"Neither sample id + repository, nor file URL have been provided dataset {dataset_id}",
        )
        return

    if dataset.source_url and (dataset.sample_id or dataset.repository_name):
        current_app.logger.info(
            f"Source URL provided together with sample ID and/or repository name for dataset {dataset_id}"
        )
        _handle_error(
            dataset,
            f"Source URL provided together with sample ID and/or repository name for dataset {dataset_id}",
        )
        return

    dataset.upload_state = "uploading"
    db.session.commit()
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
        current_app.logger.info(f"Connection failure: {str(err)}")
        _handle_error(
            dataset, f"Connection to external server failed at some point: {str(err)}"
        )
    except download_utils.DownloadUtilsException as err:
        current_app.logger.info(str(err))
        _handle_error(dataset, str(err))
        return

    db.session.commit()

    valid = dataset.validate_dataset(delete=True)
    if not valid:
        current_app.logger.info(f"Dataset {dataset.id} file was invalid.")
        _handle_error(dataset, "File formatting was invalid.")
        return

    dataset.upload_state = "uploaded"
    db.session.commit()
    dataset.preprocess_dataset()
    db.session.commit()
    _send_notification(
        dataset, "Dataset file download was successful!<br>Ready for preprocessing."
    )  # TODO preprocessing ambiguous
    current_app.logger.info("Success.")
    pipeline_steps.set_task_progress(100)


def _handle_error(dataset: Dataset, msg: str):
    _send_notification(dataset, f"Dataset creation failed:<br>{msg}", "failed")
    pipeline_steps.set_task_progress(100)

    db.session.delete(dataset)
    db.session.commit()


def _send_notification(dataset: Dataset, msg: str, status: str = "success"):
    notification_handler.send_notification_general(
        {
            "id": -1 if get_current_job() is None else get_current_job().get_id(),
            "dataset_name": dataset.dataset_name,
            "time": datetime.now(),
            "notification_type": "upload_notification",
            "owner": dataset.user.id,
            "message": msg,
            "status": status,
        }
    )
