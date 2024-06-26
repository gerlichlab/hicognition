"""Pipeline steps for redis queue"""
import os
import uuid
import logging
from datetime import datetime
from flask.globals import current_app
import pandas as pd
import numpy as np
from rq import get_current_job
from . import db
from . import pipeline_worker_functions as worker_funcs
from .notifications import NotificationHandler
from .models import (
    Dataset,
    Collection,
    Intervals,
    Task,
    dataset_preprocessing_table,
    dataset_failed_table,
    collections_failed_table,
    collections_preprocessing_table,
)

# set up notification handler

notification_handler = NotificationHandler()


def bed_preprocess_pipeline_step(dataset_id, windowsize):
    """
    Performs preprocessing pipeline step for bed and bedpe:
    * Create downsampled indices
    * add Intervals dataset entry
    """
    current_app.logger.info(f"  Generating Intervals: {dataset_id} with {windowsize}")
    # get database object
    dataset = Dataset.query.get(dataset_id)

    # read bed(pe) file
    bed_path = dataset.file_path
    bed_bedpe = pd.read_csv(bed_path, sep="\t", header=None)
    index_file = os.path.join(
        current_app.config["UPLOAD_DIR"], bed_path.split(os.sep)[-1] + "_indices.npy"
    )
    if len(bed_bedpe) < current_app.config["STACKUP_THRESHOLD"]:
        # if there are less rows than the stackup theshold, index file are the indices of this file
        sub_sample_index = np.arange(len(bed_bedpe))
    else:
        # set random seed
        np.random.seed(42)
        # subsample
        all_indices = np.arange(len(bed_bedpe))
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
    current_app.logger.info(
        f"  Doing pileup on cooler {cooler_dataset_id} with intervals { interval_id} on binsize {binsize} with {pileup_type}"
    )
    cooler_dataset = Dataset.query.get(cooler_dataset_id)
    intervals = Intervals.query.get(interval_id)
    # get path to interval regions
    regions_path = intervals.source_dataset.file_path
    # get dimension
    dimension = intervals.source_dataset.dimension
    # do pileup
    current_app.logger.debug(
        f"      {cooler_dataset_id}-{interval_id}-{binsize}|{pileup_type} => Doing pileup..."
    )
    # get windowsize
    window_size = intervals.windowsize
    if window_size is not None:
        # check whether windowsize is divisible by binsize
        if window_size % int(binsize) != 0:
            current_app.logger.warn(
                f"      {cooler_dataset_id}-{interval_id}-{binsize}|{pileup_type} => ########### Windowsize and binsize do not match! ##############"
            )
            return
        pileup_array = worker_funcs._do_pileup_fixed_size(
            cooler_dataset,
            window_size,
            binsize,
            regions_path,
            arms,
            pileup_type,
            collapse=False,
            dimension=dimension,
        )
    else:
        pileup_array = worker_funcs._do_pileup_variable_size(
            cooler_dataset,
            binsize,
            regions_path,
            arms,
            pileup_type,
            collapse=False,
            dimension=dimension,
        )
    embedding_results = worker_funcs._do_embedding_2d(pileup_array)
    # add result to database
    current_app.logger.debug(
        f"      {cooler_dataset_id}-{interval_id}-{binsize}|{pileup_type} => Writing output..."
    )
    file_name = uuid.uuid4().hex + ".npy"
    file_path = os.path.join(current_app.config["UPLOAD_DIR"], file_name)
    np.save(file_path, np.nanmean(pileup_array, axis=2))
    # add this to database
    current_app.logger.debug(
        f"      {cooler_dataset_id}-{interval_id}-{binsize}|{pileup_type} => Adding database entry for pileup..."
    )
    worker_funcs._add_pileup_db(
        file_path, binsize, intervals.id, cooler_dataset.id, pileup_type
    )
    # add database entry for embedding
    file_path_embedding = os.path.join(
        current_app.config["UPLOAD_DIR"], uuid.uuid4().hex + "_embedding.npy"
    )
    np.save(file_path_embedding, embedding_results["embedding"])
    # write output for cluster ids
    for size in ["small", "large"]:
        file_path_cluster_ids = os.path.join(
            current_app.config["UPLOAD_DIR"],
            uuid.uuid4().hex + f"_cluster_ids_{size}.npy",
        )
        np.save(
            file_path_cluster_ids, embedding_results["clusters"][size]["cluster_ids"]
        )
        # write output for thumbnails
        file_path_thumbnails = os.path.join(
            current_app.config["UPLOAD_DIR"],
            uuid.uuid4().hex + f"_thumbnails_{size}.npy",
        )
        np.save(file_path_thumbnails, embedding_results["clusters"][size]["thumbnails"])
        filepaths = {
            "embedding": file_path_embedding,
            "cluster_ids": file_path_cluster_ids,
            "thumbnails": file_path_thumbnails,
        }
        # add to database
        worker_funcs._add_embedding_2d_to_db(
            filepaths, binsize, intervals.id, cooler_dataset.id, pileup_type, size
        )
    current_app.logger.info(
        f"       {cooler_dataset_id}-{interval_id}-{binsize}|{pileup_type} => Success!"
    )


def stackup_pipeline_step(bigwig_dataset_id, intervals_id, binsize, region_side=None):
    """Performs stackup of bigwig dataset over the intervals provided with the indicated binsize.
    Stores result and adds it to database."""
    current_app.logger.info(
        f"  Doing pileup on bigwig {bigwig_dataset_id} with intervals {intervals_id} on binsize {binsize} with region_side: {region_side}"
    )
    bigwig_dataset = Dataset.query.get(bigwig_dataset_id)
    intervals = Intervals.query.get(intervals_id)
    # get path to dataset
    file_path = intervals.source_dataset.file_path
    # get windowsize
    window_size = intervals.windowsize
    # load bedfile
    current_app.logger.debug(
        f"      {bigwig_dataset_id}-{intervals_id}-{binsize} => Loading regions..."
    )
    regions = pd.read_csv(file_path, sep="\t", header=None)
    sub_sample_index = np.load(intervals.file_path_sub_sample_index)
    regions_small = regions.iloc[sub_sample_index, :]
    current_app.logger.debug(
        f"      {bigwig_dataset_id}-{intervals_id}-{binsize} => Doing stackup..."
    )
    if window_size is None:
        full_size_array = worker_funcs._do_stackup_variable_size(
            bigwig_dataset.file_path, regions, binsize, region_side
        )
        downsampled_array = worker_funcs._do_stackup_variable_size(
            bigwig_dataset.file_path, regions_small, binsize, region_side
        )
    else:
        full_size_array = worker_funcs._do_stackup_fixed_size(
            bigwig_dataset.file_path, regions, window_size, binsize, region_side
        )
        downsampled_array = worker_funcs._do_stackup_fixed_size(
            bigwig_dataset.file_path, regions_small, window_size, binsize, region_side
        )
    # save full length array to file
    current_app.logger.debug(
        f"      {bigwig_dataset_id}-{intervals_id}-{binsize} => Writing output..."
    )
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
    current_app.logger.debug(
        f"      {bigwig_dataset_id}-{intervals_id}-{binsize} => Adding database entry..."
    )
    worker_funcs._add_stackup_db(
        file_path,
        file_path_small,
        binsize,
        intervals.id,
        bigwig_dataset.id,
        region_side,
    )
    worker_funcs._add_line_db(
        file_path_line, binsize, intervals.id, bigwig_dataset.id, region_side
    )
    current_app.logger.info(
        f"       {bigwig_dataset_id}-{intervals_id}-{binsize} => Success!"
    )


def enrichment_pipeline_step(collection_id, intervals_id, binsize, region_side=None):
    """Pipeline step to perform enrichment analysis"""
    current_app.logger.info(
        f"Doing enrichment analysis with collection {collection_id} on intervals {intervals_id} with binsize {binsize} with region_side: {region_side}"
    )
    # get query regions
    intervals = Intervals.query.get(intervals_id)
    file_path = intervals.source_dataset.file_path
    window_size = intervals.windowsize
    regions_path = intervals.source_dataset.file_path
    if window_size is None:
        stacked = worker_funcs._do_enrichment_calculations_variable_size(
            collection_id, binsize, regions_path, region_side=region_side
        )
    else:
        stacked = worker_funcs._do_enrichment_calculations_fixed_size(
            collection_id, window_size, binsize, regions_path, region_side=region_side
        )
    # write output
    current_app.logger.debug(
        f"      {collection_id}-{intervals_id}-{binsize} => Writing output..."
    )
    file_path = os.path.join(
        current_app.config["UPLOAD_DIR"], uuid.uuid4().hex + ".npy"
    )
    np.save(file_path, stacked)
    # add to database
    worker_funcs._add_association_data_to_db(
        file_path, binsize, intervals_id, collection_id, region_side=region_side
    )
    current_app.logger.info(
        f"      {collection_id}-{intervals_id}-{binsize} => Success!"
    )


def embedding_1d_pipeline_step(collection_id, intervals_id, binsize, region_side=None):
    """Performs embedding on each binsize-sized bin of the window specified in intervals_id using
    the features in collection_id"""
    current_app.logger.info(
        f"Doing 1d-embedding with collection {collection_id} on intervals {intervals_id} with binsize {binsize} with region_side: {region_side}"
    )
    # get intervals to decide whether fixed size or variable size
    intervals = Intervals.query.get(intervals_id)
    if intervals.windowsize is None:
        embedding_results = worker_funcs._do_embedding_1d_variable_size(
            collection_id, intervals_id, binsize, region_side=region_side
        )
    else:
        embedding_results = worker_funcs._do_embedding_1d_fixed_size(
            collection_id, intervals_id, binsize, region_side=region_side
        )
    # write output for embedding
    current_app.logger.debug(
        f"      {collection_id}-{intervals_id}-{binsize} => Writing output..."
    )
    file_path_embedding = os.path.join(
        current_app.config["UPLOAD_DIR"], uuid.uuid4().hex + "_embedding.npy"
    )
    np.save(file_path_embedding, embedding_results["embedding"])
    # write output for feature_overlay
    file_path_features = os.path.join(
        current_app.config["UPLOAD_DIR"], uuid.uuid4().hex + "_features.npy"
    )
    np.save(file_path_features, embedding_results["features"])
    # write output for clusters
    for size in ["small", "large"]:
        file_path_cluster_ids = os.path.join(
            current_app.config["UPLOAD_DIR"],
            uuid.uuid4().hex + f"_cluster_ids_{size}.npy",
        )
        np.save(
            file_path_cluster_ids, embedding_results["clusters"][size]["cluster_ids"]
        )
        # write output for average_features
        file_path_average_values = os.path.join(
            current_app.config["UPLOAD_DIR"],
            uuid.uuid4().hex + f"_average_values_{size}.npy",
        )
        np.save(
            file_path_average_values,
            embedding_results["clusters"][size]["average_values"],
        )
        filepaths = {
            "embedding": file_path_embedding,
            "cluster_ids": file_path_cluster_ids,
            "average_values": file_path_average_values,
            "features": file_path_features,
        }
        # add to database
        worker_funcs._add_embedding_1d_to_db(
            filepaths, binsize, intervals.id, collection_id, size, region_side
        )
    current_app.logger.info(
        f"      {collection_id}-{intervals_id}-{binsize} => Success!"
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
            & (Task.complete.is_(False))
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
        # signal completion
        dataset = Dataset.query.get(dataset_id)
        current_app.logger.debug("      Signalling reached")
        notification_handler.signal_processing_update(
            {
                "data_type": dataset.filetype,
                "name": dataset.dataset_name,
                "processing_type": current_app.config["PIPELINE_NAMES"][
                    dataset.filetype
                ][0],
                "owner": Task.query.get(get_current_job().get_id()).user_id,
                "region_id": region.id,
                "region_name": region.dataset_name,
                "time": datetime.now(),
                "notification_type": "processing_finished",
                "id": get_current_job().get_id(),
            }
        )


def set_task_progress(progress):
    """Sets the progress of the task."""
    job = get_current_job()
    if job:
        job.meta["progress"] = progress
        job.save_meta()
        task = Task.query.get(job.get_id())
        if progress >= 100 and (task is not None):  # CRITICAL run condition!
            task.complete = True
            db.session.commit()


def set_dataset_failed(dataset_id, intervals_id):
    """Adds feature dataset associated with dataset_id to failed datasets of region ds associated with intervals_id"""
    current_app.logger.error("      Preprocessing failed")
    feature = Dataset.query.get(dataset_id)
    region = Intervals.query.get(intervals_id).source_dataset
    current_app.logger.error(
        f"      Region: {region} with processing features {region.processing_features} and dataset {feature}"
    )
    # remove feature from preprocessing list
    # -> this needs to be done on the association table to avoid concurrency problems
    stmt = dataset_preprocessing_table.delete().where(
        db.and_(
            (dataset_preprocessing_table.c.dataset_region == region.id),
            (dataset_preprocessing_table.c.dataset_feature == feature.id),
        )
    )
    db.session.execute(stmt)
    db.session.commit()
    # add region to failed_features -
    # > if this combination is already in, this operation will fail, but the first one will succeed
    try:
        stmt = dataset_failed_table.insert().values(
            dataset_region=region.id, dataset_feature=feature.id
        )
        db.session.execute(stmt)
        db.session.commit()
        # signal failure
        dataset = Dataset.query.get(dataset_id)
        current_app.logger.debug("      Signalling reached")
        notification_handler.signal_processing_update(
            {
                "data_type": dataset.filetype,
                "name": dataset.dataset_name,
                "processing_type": current_app.config["PIPELINE_NAMES"][
                    dataset.filetype
                ][0],
                "owner": Task.query.get(get_current_job().get_id()).user_id,
                "region_id": region.id,
                "region_name": region.dataset_name,
                "time": datetime.now(),
                "notification_type": "processing_failed",
                "id": get_current_job().get_id(),
            }
        )
    except BaseException as err:
        current_app.logger.error(err, exc_info=True)
    current_app.logger.error("      Setting for fail finished")


def set_collection_failed(collection_id, intervals_id):
    """Adds collection with collection_id to failed collections of region ds associated with intervals"""
    current_app.logger.error("      Set for fail")
    collection = Collection.query.get(collection_id)
    region = Intervals.query.get(intervals_id).source_dataset
    current_app.logger.error(
        f"      Region: {region} with processing collections {region.processing_collections} and collection {collection}"
    )
    # remove feature from preprocessing list
    # -> this needs to be done on the association table to avoid concurrency problems
    stmt = collections_preprocessing_table.delete().where(
        db.and_(
            (collections_preprocessing_table.c.dataset_region == region.id),
            (collections_preprocessing_table.c.collection_feature == collection.id),
        )
    )
    db.session.execute(stmt)
    db.session.commit()
    # add region to failed_features
    # -> if this combination is already in, this operation will fail, but the first one will succeed
    try:
        stmt = collections_failed_table.insert().values(
            dataset_region=region.id, collection_feature=collection.id
        )
        db.session.execute(stmt)
        db.session.commit()
        notification_handler.signal_processing_update(
            {
                "data_type": collection.kind,
                "name": collection.name,
                "processing_type": current_app.config["PIPELINE_NAMES"]["collections"][
                    collection.kind
                ][0],
                "owner": Task.query.get(get_current_job().get_id()).user_id,
                "region_id": region.id,
                "region_name": region.dataset_name,
                "time": datetime.now(),
                "notification_type": "processing_failed",
                "id": get_current_job().get_id(),
            }
        )
    except BaseException as err:
        current_app.logger.error(err, exc_info=True)
    current_app.logger.error("      Setting for fail finished")


def set_collection_finished(collection_id, intervals_id):
    """removes dataset from region associated with intervals_id if no other task is associated with it."""
    region = Intervals.query.get(intervals_id).source_dataset
    associated_tasks = (
        Task.query.join(Intervals)
        .join(Dataset)
        .filter(
            (Dataset.id == region.id)
            & (Task.collection_id == collection_id)
            & (Task.complete.is_(False))
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
        # signal completion
        collection = Collection.query.get(collection_id)
        # get owner of task
        if get_current_job() is None:
            owner = 0
            job_id = "undefined"
        else:
            owner = Task.query.get(get_current_job().get_id()).user_id
            job_id = get_current_job().get_id()
        # send notification
        notification_handler.signal_processing_update(
            {
                "data_type": collection.kind,
                "name": collection.name,
                "processing_type": current_app.config["PIPELINE_NAMES"]["collections"][
                    collection.kind
                ][0],
                "owner": owner,
                "region_id": region.id,
                "region_name": region.dataset_name,
                "time": datetime.now(),
                "notification_type": "processing_finished",
                "id": job_id,
            }
        )
