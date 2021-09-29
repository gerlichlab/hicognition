"""Pipeline steps for redis queue"""
import os
import uuid
import logging

from flask.globals import current_app
import pandas as pd
import numpy as np
from . import db
from . import pipeline_worker_functions as worker_funcs
from rq import get_current_job
from . import db
from .models import (
    Collection,
    Dataset,
    Intervals,
    Task,
    dataset_preprocessing_table,
    collections_preprocessing_table,
)

# get logger
log = logging.getLogger("rq.worker")


def bed_preprocess_pipeline_step(dataset_id, windowsize):
    """
    Performs bedpe preprocessing pipeline step:
    * Convert bed to bedpe
    * Create downsampled indices
    * add Intervals dataset entry
    """
    log.info(f"  Generating Intervals: {dataset_id} with {windowsize}")
    # get database object
    dataset = Dataset.query.get(dataset_id)
    bed_path = dataset.file_path
    bed = pd.read_csv(bed_path, sep="\t", header=None)
    index_file = os.path.join(
        current_app.config["UPLOAD_DIR"], bed_path.split(os.sep)[-1] + "_indices.npy"
    )
    if len(bed) < current_app.config["STACKUP_THRESHOLD"]:
        # if there are less rows than the stackup theshold, index file are the indices of this file
        sub_sample_index = np.arange(len(bed))
    else:
        # set random seed
        np.random.seed(42)
        # subsample
        all_indices = np.arange(len(bed))
        sub_sample_index = np.random.choice(
            all_indices, current_app.config["STACKUP_THRESHOLD"], replace=False
        )
    # store indices
    np.save(index_file, sub_sample_index)
    # Commit to database
    if windowsize == "variable":
        windowsize = None
    new_entry = Intervals(
        dataset_id=dataset_id,
        name=dataset.dataset_name + f"_{windowsize}",
        file_path_sub_sample_index=index_file,
        windowsize=windowsize,
    )
    db.session.add(new_entry)
    db.session.commit()


def pileup_pipeline_step(cooler_dataset_id, interval_id, binsize, arms, pileup_type):
    """Performs pileup [either ICCF or Obs/Exp; parameter passed to pileup_type] of cooler_dataset on
    intervals with resolution binsize."""
    log.info(
        f"  Doing pileup on cooler {cooler_dataset_id} with intervals { interval_id} on binsize {binsize}"
    )
    cooler_dataset = Dataset.query.get(cooler_dataset_id)
    intervals = Intervals.query.get(interval_id)
    # get path to interval regions
    regions_path = intervals.source_dataset.file_path
    # do pileup
    log.info("      Doing pileup...")
    # get windowsize
    window_size = intervals.windowsize
    if window_size is not None:
        # check whether windowsize is divisible by binsize
        if window_size % int(binsize) != 0:
            log.warn(
                "      ########### Windowsize and binsize do not match! ##############"
            )
            return
        pileup_array = worker_funcs._do_pileup_fixed_size(
            cooler_dataset, window_size, binsize, regions_path, arms, pileup_type
        )
    else:
        pileup_array = worker_funcs._do_pileup_variable_size(
            cooler_dataset, binsize, regions_path, arms, pileup_type
        )
    # add result to database
    log.info("      Writing output...")
    file_name = uuid.uuid4().hex + ".npy"
    file_path = os.path.join(current_app.config["UPLOAD_DIR"], file_name)
    np.save(file_path, pileup_array)
    # add this to database
    log.info("      Adding database entry...")
    worker_funcs._add_pileup_db(
        file_path, binsize, intervals.id, cooler_dataset.id, pileup_type
    )
    log.info("      Success!")


def stackup_pipeline_step(bigwig_dataset_id, intervals_id, binsize):
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
    if window_size is None:
        full_size_array = worker_funcs._do_stackup_variable_size(
            bigwig_dataset.file_path, regions, binsize, 
        )
        downsampled_array = worker_funcs._do_stackup_variable_size(
            bigwig_dataset.file_path, regions_small, binsize, 
        )
    else:
        full_size_array = worker_funcs._do_stackup_fixed_size(
            bigwig_dataset.file_path, regions, window_size, binsize
        )
        downsampled_array = worker_funcs._do_stackup_fixed_size(
            bigwig_dataset.file_path, regions_small, window_size, binsize
        )
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
    file_path_small = os.path.join(current_app.config["UPLOAD_DIR"], file_name_small)
    np.save(file_path_small, downsampled_array)
    # add to database
    log.info("      Adding database entry...")
    worker_funcs._add_stackup_db(
        file_path, file_path_small, binsize, intervals.id, bigwig_dataset.id
    )
    worker_funcs._add_line_db(file_path_line, binsize, intervals.id, bigwig_dataset.id)
    log.info("      Success!")


def enrichment_pipeline_step(collection_id, intervals_id, binsize):
    """Pipeline step to perform enrichment analysis"""
    log.info(
        f"Doing enrichment analysis with collection {collection_id} on intervals {intervals_id} with binsize {binsize}"
    )
    # get query regions
    intervals = Intervals.query.get(intervals_id)
    file_path = intervals.source_dataset.file_path
    window_size = intervals.windowsize
    regions_path = intervals.source_dataset.file_path
    if window_size is None:
        stacked = worker_funcs._do_enrichment_calculations_variable_size(
            collection_id, binsize, regions_path
        )
    else:
        stacked = worker_funcs._do_enrichment_calculations_fixed_size(
            collection_id, window_size, binsize, regions_path
        )
    # write output
    log.info("      Writing output...")
    file_path = os.path.join(
        current_app.config["UPLOAD_DIR"], uuid.uuid4().hex + ".npy"
    )
    np.save(file_path, stacked)
    # add to database
    worker_funcs._add_association_data_to_db(
        file_path, binsize, intervals_id, collection_id
    )


def perform_1d_embedding(collection_id, intervals_id, binsize):
    """Performs embedding on each binsize-sized bin of the window specified in intervals_id using
    the features in collection_id"""
    # get intervals to decide whether fixed size or variable size
    intervals = Intervals.query.get(intervals_id)
    if intervals.windowsize is None:
        embedding, feature_frame = worker_funcs._do_embedding_1d_variable_size(
            collection_id, intervals_id, binsize
        )
    else:
        embedding, feature_frame = worker_funcs._do_embedding_1d_fixed_size(
            collection_id, intervals_id, binsize
        )
    # write output for embedding
    log.info("      Writing output...")
    file_path = os.path.join(
        current_app.config["UPLOAD_DIR"], uuid.uuid4().hex + "_embedding.npy"
    )
    np.save(file_path, embedding)
    # write output for feature_overlay
    file_path_features = os.path.join(
        current_app.config["UPLOAD_DIR"], uuid.uuid4().hex + "_features.npy"
    )
    np.save(file_path_features, feature_frame)
    # add to database
    worker_funcs._add_embedding_1d_to_db(
        file_path, file_path_features, binsize, intervals_id, collection_id
    )


def set_dataset_finished(dataset_id, intervals_id):
    """removes dataset from region associated with intervals_id if no other task is associated with it."""
    region = Intervals.query.get(intervals_id).source_dataset
    associated_tasks = (
        Task.query.join(Intervals)
        .join(Dataset)
        .filter(
            (Dataset.id == region.id)
            & (Task.dataset_id == dataset_id)
            & (Task.complete == False)
        )
        .all()
    )
    if len(associated_tasks) == 0:
        # current task is last task, remove feature
        stmt = dataset_preprocessing_table.delete().where(
            db.and_(
                (dataset_preprocessing_table.c.dataset_region == region.id),
                (dataset_preprocessing_table.c.dataset_feature == dataset_id),
            )
        )
        db.session.execute(stmt)
        db.session.commit()


def set_task_progress(progress):
    job = get_current_job()
    if job:
        job.meta["progress"] = progress
        job.save_meta()
        task = Task.query.get(job.get_id())
        if progress >= 100:
            task.complete = True
            db.session.commit()


def set_dataset_failed(dataset_id, intervals_id):
    """Adds feature dataset associated with dataset_id to failed datasets of region ds associated with intervals_id"""
    log.error("      Preprocessing failed")
    feature = Dataset.query.get(dataset_id)
    region = Intervals.query.get(intervals_id).source_dataset
    log.error(
        f"      Region: {region} with processing features {region.processing_features} and dataset {feature}"
    )
    # remove feature from preprocessing list -> this needs to be done on the association table to avoid concurrency problems
    stmt = dataset_preprocessing_table.delete().where(
        db.and_(
            (dataset_preprocessing_table.c.dataset_region == region.id),
            (dataset_preprocessing_table.c.dataset_feature == feature.id),
        )
    )
    db.session.execute(stmt)
    db.session.commit()
    # add region to failed_features -> if this combination is already in, this operation will fail, but the first one will succeed
    try:
        region.failed_features.append(feature)
        db.session.commit()
    except BaseException as e:
        log.error(e, exc_info=True)
    log.error("      Setting for fail finished")


def set_collection_failed(collection_id, intervals_id):
    """Adds collection with collection_id to failed collections of region ds associated with intervals"""
    log.error("      Set for fail")
    collection = Collection.query.get(collection_id)
    region = Intervals.query.get(intervals_id).source_dataset
    log.error(
        f"      Region: {region} with processing collections {region.processing_collections} and collection {collection}"
    )
    # remove feature from preprocessing list -> this needs to be done on the association table to avoid concurrency problems
    stmt = collections_preprocessing_table.delete().where(
        db.and_(
            (collections_preprocessing_table.c.dataset_region == region.id),
            (collections_preprocessing_table.c.collection_feature == collection.id),
        )
    )
    db.session.execute(stmt)
    db.session.commit()
    # add region to failed_features -> if this combination is already in, this operation will fail, but the first one will succeed
    try:
        region.failed_collections.append(collection)
        db.session.commit()
    except BaseException as e:
        log.error(e, exc_info=True)
    log.error("      Setting for fail finished")


def set_collection_finished(collection_id, intervals_id):
    """removes dataset from region associated with intervals_id if no other task is associated with it."""
    region = Intervals.query.get(intervals_id).source_dataset
    associated_tasks = (
        Task.query.join(Intervals)
        .join(Dataset)
        .filter(
            (Dataset.id == region.id)
            & (Task.collection_id == collection_id)
            & (Task.complete == False)
        )
        .all()
    )
    if len(associated_tasks) == 0:
        # current task is last task, remove feature
        stmt = collections_preprocessing_table.delete().where(
            db.and_(
                (collections_preprocessing_table.c.dataset_region == region.id),
                (collections_preprocessing_table.c.collection_feature == collection_id),
            )
        )
        db.session.execute(stmt)
        db.session.commit()