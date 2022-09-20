"""Tasks for the redis-queue"""
import os
import logging
from flask import current_app
from matplotlib.pyplot import switch_backend
from werkzeug.utils import secure_filename
import pandas as pd
import requests
import gzip
import json
from hicognition import io_helpers
from . import create_app, db
from .models import Assembly, Dataset, IndividualIntervalData, Collection, User, DataRepository, User_DataRepository_Credentials
from . import pipeline_steps
from .notifications import NotificationHandler
from . import file_handler
#from api import get_routes
from api.get_routes import get_ENCODE_metadata

# get logger
log = logging.getLogger("rq.worker")

# setup app context

app = create_app(os.getenv("FLASK_CONFIG") or "default")
app.app_context().push()

# set up notification handler

notifcation_handler = NotificationHandler()

# set basedir

basedir = os.path.abspath(os.path.dirname(__file__)) # TODO unused


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

def download_dataset_file(dataset_id, delete_if_invalid=False): # TODO file_path should not be here. You should define a temp file path for stuff that might get deleted or gunzipped
    """
    Downloads dataset file from web and validates + 'preprocesses' it.
    ua
    - ua: have put this in tasks, as this made most sense.
    - ua: I would actually put this into the dataset class if possible.
    - this fnct is not using the REST API provided by 4dn
        as it is meant for submission
    """
    ds = db.session.query(Dataset).get(dataset_id)
    log.info(f'Starting download routine for dataset {ds.id}')
    # if download is from known repository, build URL
    metadata = get_ENCODE_metadata(ds.repository.name, ds.sample_id)
    metadata = json.loads(metadata)
    
    if metadata['status'] == 'sample_not_found':
        log.info(f'      Sample does not exist.')
        return
    if metadata['status'] == 'api_credentials_wrong':
        log.info(f'      API credentials invalid.')
        return
    
    if metadata['json'].get('open_data_url'):
        ds.source_url = metadata['json']['open_data_url']
    else:
        ds.source_url = metadata['json']['href']
        
    md5 = metadata['json']['md5sum']

    # download file and put into variable content
    try:
        file_name, content = file_handler.download_file(ds.source_url)
    except requests.HTTPError as err:
        log.info(f"       HTTP Error: {err}")
        ds.processing_status = "file not found"
        ds.file_path = ""
        db.session.commit()
        return

    if not file_name:
        file_name = secure_filename(f"{ds.user.id}_{metadata['json']['display_title']}") # contains file_name with ext

    # check if compressed and decompress
    if file_name.lower().endswith('.gz'):
        content = gzip.decompress(content)
        file_name = file_name[:-3] # strip the gz

    ds.file_path = os.path.join(current_app.config["UPLOAD_DIR"], file_name)

    # save file
    file_handler.save_file(ds.file_path, content, overwrite=False)
    ds.processing_state = "uploaded"
    db.session.commit()

    # TODO notification management > what it fails, success or similar?
    valid = ds.validate_dataset() #  TODO can't delete file/object, bc user would not get info about it then
    if not valid:
        log.info(f'      Dataset file was invalid.')
        return -1 #  dont' have to return anything

    ds.preprocess_dataset() #  TODO can't delete file/object, bc user would not get info about it then
    db.session.commit()
    pipeline_steps.set_task_progress(100)
    log.info("      Success.")

def handle_new_file():
    pass