"""Tasks for the redis-queue"""
import os
import logging


import pandas as pd
from hicognition import io_helpers
from . import create_app, db
from .models import Dataset, IndividualIntervalData, Collection
from . import pipeline_steps
from .api.helpers import remove_safely

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
    - Indicate in Job table in database that job is complete.
    Output-folder is not needed for this since the file_path
    of Dataset entry contains it.
    """
    window_sizes = app.config["PREPROCESSING_MAP"].keys()
    log.info(f"Bed pipeline started for {dataset_id} with {window_sizes}")
    # bed-file preprocessing: sorting, clodius, uploading to higlass
    file_path = Dataset.query.get(dataset_id).file_path
    # clean dataset
    log.info("      Clean...")
    cleaned_file_name = file_path.split(".")[0] + "_cleaned.bed"
    io_helpers.clean_bed(file_path, cleaned_file_name)
    # set cleaned_file_name as file_name
    dataset_object = Dataset.query.get(dataset_id)
    dataset_object.file_path = cleaned_file_name
    # delete old file
    log.info("      Delete Unsorted...")
    remove_safely(file_path)
    db.session.commit()
    for window in window_sizes:
        # preprocessing
        pipeline_steps.bed_preprocess_pipeline_step(dataset_id, window)
    pipeline_steps._set_task_progress(100)


def pipeline_pileup(dataset_id, intervals_id, binsize):
    """Start pileup pipeline for specified combination of
    dataset_id (cooler_file), binsize and intervals_id"""
    chromosome_arms = pd.read_csv(app.config["CHROM_ARMS"])
    pipeline_steps.perform_pileup(
        dataset_id, intervals_id, binsize, chromosome_arms, "ICCF"
    )
    pipeline_steps.perform_pileup(
        dataset_id, intervals_id, binsize, chromosome_arms, "Obs/Exp"
    )
    pipeline_steps._set_task_progress(100)


def pipeline_stackup(dataset_id, intervals_id, binsize):
    """Start stackup pipeline for specified combination of
    dataset_id (bigwig file), binsize and intervals_id"""
    pipeline_steps.perform_stackup(dataset_id, intervals_id, binsize)
    pipeline_steps._set_task_progress(100)


def pipeline_lola(collection_id, intervals_id, binsize):
    """Starts lola enrichment calculation pipeline step for a specific
    collection_id, binsize and intervals_id"""
    pipeline_steps.perform_enrichment_analysis(collection_id, intervals_id, binsize)
    pipeline_steps._set_task_progress(100)

def pipeline_embedding_1d(collection_id, intervals_id, binsize):
    """Starts embedding pipeline steps for feature collections refering to
    1 dimensional features per regions (e.g. bigwig tracks)"""
    # check whether stackups exist and perform stackup if not
    for source_dataset in Collection.query.get(collection_id).datasets:
        stackup = IndividualIntervalData.query.filter((IndividualIntervalData.dataset_id == source_dataset.id)
                                                     & (IndividualIntervalData.intervals_id == intervals_id)
                                                     & (IndividualIntervalData.binsize == binsize)).first()
        if stackup is None:
            pipeline_steps.perform_stackup(source_dataset.id, intervals_id, binsize)
    # perform embedding
    pipeline_steps.perform_1d_embedding(collection_id, intervals_id, binsize)
