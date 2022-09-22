"""Tasks for the redis-queue"""
import hashlib
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

notifcation_handler = NotificationHandler()

# set basedir

basedir = os.path.abspath(os.path.dirname(__file__)) # TODO unused

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
def download_dataset_file(dataset_id: int, delete_if_invalid: bool = False):
    """
    Downloads dataset file from web and validates + 'preprocesses' it.
    ua
    - ua: have put this in tasks, as this made most sense.
    - ua: I would actually put this into the dataset class if possible.
    - this fnct is not using the REST API provided by 4dn
        as it is meant for submission
    """
    ds = Dataset.query.get(dataset_id)
    if not (ds.sample_id and ds.repository) and not ds.source_url:
        log.info(f'No sample_id, repo_name or source_url provided for {ds.id}')
        return True
    
    is_repository = ds.sample_id and ds.repository
    download_func = download_utils.download_encode if is_repository else download_utils.download_url
    
    try:
        if is_repository:
            download_utils.download_encode(ds, current_app.config["UPLOAD_DIR"])
        else:
            download_utils.download_url(ds, current_app.config["UPLOAD_DIR"], current_app.config["DATASET_OPTION_MAPPING"][ds.file_type])
    except requests.HTTPError as err: # TODO notifactions
        log.info(f"       HTTP Error: {err}")
        ds.processing_state = "file not found"
        ds.file_path = ""
        db.session.commit()
        return
    finally:
        db.session.commit()
    
    valid = ds.validate_dataset() #  TODO can't delete file/object, bc user would not get info about it then
    if not valid:
        log.info(f'      Dataset file was invalid.')
        ds.processing_state = "file not found"
        return

    ds.preprocess_dataset()
    db.session.commit()
    pipeline_steps.set_task_progress(100)
    log.info("      Success.")
    
    # log.info(f'Starting download routine for dataset {ds.id}')
    # # if sample_id and repository_name is specified, get data from repo
    # if is_repository:
    #     log.info(f'Getting metadata for {ds.id} from {ds.repository.name}')
        
    #     metadata = file_utils.download_ENCODE_metadata(ds.repository.name, ds.sample_id)
    #     metadata = json.loads(metadata)
        
    #     if metadata['status'] == 'sample_not_found':
    #         log.info(f'      Sample does not exist.')
    #         return
    #     if metadata['status'] == 'api_credentials_wrong':
    #         log.info(f'      API credentials invalid.')
    #         return
        
    #     ds.source_url = metadata['json'].get('open_data_url')
    #     # elif metadata['json'].get('href'):
    #     #     ds.source_url = metadata['json']['href'] # TODO make way to attach href to the repo url
    #     if ds.source_url is None:
    #         log.info(f'      Could not find URL in json.')
    #         return # TODO notification, task process status
        
    #     md5 = metadata['json'].get('md5sum')
    #     file_name = metadata['json'].get('display_title')
    # else:
    #     file_name = f'{ds.name}.{current_app.config["DATASET_OPTION_MAPPING"][ds.file_type]}'

    # # download file and put into variable content
    # try:
    #     http_file_name, http_content = download_utils.download_file(ds.source_url)
    #     file_name = http_file_name if http_file_name is not None else file_name
    # except requests.HTTPError as err:
    #     log.info(f"       HTTP Error: {err}")
    #     ds.processing_state = "file not found"
    #     ds.file_path = ""
    # finally:
    #     db.session.commit()
    
    # if md5 is not None and hashlib.md5(http_content) != md5:
    #     log.info(f'      md5 checksum and md5(file content) not equal')
    #     ds.processing_state = "checksum failed"
    #     ds.file_path = ""
    #     db.session.commit()
    #     return

    # file_name = secure_filename(f"{ds.user.id}_{file_name}") # contains file_name with ext
    # file_name = file_name[:-3] if file_name.lower().endswith('.gz') else file_name
    
    # # check if compressed and decompress
    # if file_utils.is_gzipped(http_content):
    #     http_content = gzip.decompress(http_content)
    
    # ds.file_path = os.path.join(current_app.config["UPLOAD_DIR"], file_name)

    # # save file
    # if os.path.exists(ds.file_path):
    #     log.error(f'      File at {ds.file_path} already exists')
    #     return # TODO notification, task process status
    
    # with open(ds.file_path, 'wb') as f_out:
    #     f_out.write(http_content)
        
    # ds.processing_state = "uploaded"
    # db.session.commit()

    # # TODO notification management > what it fails, success or similar?
    # valid = ds.validate_dataset() #  TODO can't delete file/object, bc user would not get info about it then
    # if not valid:
    #     log.info(f'      Dataset file was invalid.')
    #     return -1 #  dont' have to return anything

    # ds.preprocess_dataset() #  TODO can't delete file/object, bc user would not get info about it then
    # db.session.commit()
    # pipeline_steps.set_task_progress(100)
    # log.info("      Success.")
