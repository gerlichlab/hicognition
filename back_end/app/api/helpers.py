"""Helper functions for api routes"""
import os
from collections import defaultdict
from flask import current_app
from ..models import (
    EmbeddingIntervalData,
    Intervals,
    Dataset,
    Collection,
    Task,
    IndividualIntervalData,
    AverageIntervalData,
    BedFileMetadata,
)
import numpy as np


def update_processing_state(entries, db):
    """updates processing state of all entries (must implement set_processing_state) in the supplied iterable"""
    for entry in entries:
        entry.set_processing_state(db)


def parse_description(form_data):
    if ("description" not in form_data) or (form_data["description"] == "null"):
        description = "No description provided"
    else:
        description = form_data["description"]
    return description

def remove_tasks(tasks, db):
    for task in tasks:
        db.session.delete(task)
    db.session.commit()


def filter_failed_tasks(tasks):
    """filters tasks for failed tasks"""
    output = []
    for task in tasks:
        if task.get_rq_job() is None:
            output.append(task)
            continue
        if task.get_rq_job().get_status() == "failed":
            output.append(task)
    return output


def remove_failed_tasks_dataset(db, dataset, region):
    """Removes all failed tasks that are associated with a particular dataset/region combination"""
    associated_tasks = (
        Task.query.join(Intervals)
        .join(Dataset)
        .filter(
            (Dataset.id == region.id)
            & (Task.dataset_id == dataset.id)
            & (Task.complete == False)
        )
        .all()
    )
    failed_tasks = filter_failed_tasks(associated_tasks)
    remove_tasks(failed_tasks, db)


def remove_failed_tasks_collection(db, collection, region):
    """Removes all failed tasks that are associated with a particular collection/region combination"""
    associated_tasks = (
        Task.query.join(Intervals)
        .join(Dataset)
        .filter(
            (Dataset.id == region.id)
            & (Task.collection_id == collection.id)
            & (Task.complete == False)
        )
        .all()
    )
    failed_tasks = filter_failed_tasks(associated_tasks)
    remove_tasks(failed_tasks, db)


def get_all_interval_ids(region_datasets):
    """Returns ids of all intervals associated with list or region datasets."""
    interval_ids = []
    for region_dataset in region_datasets:
        interval_ids.extend([entry.id for entry in region_dataset.intervals.all()])
    return interval_ids


def parse_binsizes(map, filetype):
    """returns needed binsizes from preprocessing map."""
    binsizes = set()
    for windowsize, bins in map.items():
        if windowsize != "variable":
            binsizes |= set(bins[filetype])
    return list(binsizes)


def add_average_data_to_preprocessed_dataset_map(
    average_interval_datasets, output_object, request_context
):
    for average in average_interval_datasets:
        dataset = Dataset.query.get(average.dataset_id)
        # check whether dataset is owned
        if dataset.is_access_denied(request_context):
            continue
        # check whether there are any uncompleted tasks for the region dataset associated with these features
        interval = Intervals.query.get(average.intervals_id)
        region_dataset = interval.source_dataset
        # check whether region_dataset is interval
        if region_dataset.sizeType == "Interval":
            windowsize = "variable"
        else:
            windowsize = interval.windowsize
        # check whether dataset is in failed or processing datasets
        if (dataset in region_dataset.processing_features) or (
            dataset in region_dataset.failed_features
        ):
            continue
        if average.value_type in ["Obs/Exp", "ICCF"]:
            output_object["pileup"][dataset.id]["name"] = dataset.dataset_name
            output_object["pileup"][dataset.id]["data_ids"][windowsize][
                average.binsize
            ][average.value_type] = str(average.id)
        else:
            output_object["lineprofile"][dataset.id]["name"] = dataset.dataset_name
            output_object["lineprofile"][dataset.id]["data_ids"][windowsize][
                average.binsize
            ] = str(average.id)


def add_individual_data_to_preprocessed_dataset_map(
    individual_interval_datasets, output_object, request_context
):
    for individual in individual_interval_datasets:
        dataset = Dataset.query.get(individual.dataset_id)
        # check whether dataset is owned
        if dataset.is_access_denied(request_context):
            continue
        # check whether there are any uncompleted tasks for the feature dataset
        interval = Intervals.query.get(individual.intervals_id)
        region_dataset = interval.source_dataset
        # check whether region_dataset is interval
        if region_dataset.sizeType == "Interval":
            windowsize = "variable"
        else:
            windowsize = interval.windowsize
        # check whether dataset is in failed or processing datasets
        if (dataset in region_dataset.processing_features) or (
            dataset in region_dataset.failed_features
        ):
            continue
        output_object["stackup"][dataset.id]["name"] = dataset.dataset_name
        output_object["stackup"][dataset.id]["data_ids"][windowsize][
            individual.binsize
        ] = str(individual.id)


def add_association_data_to_preprocessed_dataset_map(
    association_interval_datasets, output_object, request_context
):
    for assoc in association_interval_datasets:
        collection = Collection.query.get(assoc.collection_id)
        # check whether collection is owned
        if collection.is_access_denied(request_context):
            continue
        # check whether there are any uncompleted tasks for the feature dataset
        interval = Intervals.query.get(assoc.intervals_id)
        region_dataset = interval.source_dataset
        # check whether region_dataset is interval
        if region_dataset.sizeType == "Interval":
            windowsize = "variable"
        else:
            windowsize = interval.windowsize
        if (collection in region_dataset.processing_collections) or (
            collection in region_dataset.failed_collections
        ):
            continue
        output_object["lola"][collection.id]["name"] = collection.name
        output_object["lola"][collection.id][
            "collection_dataset_names"
        ] = collection.to_json()["dataset_names"]
        output_object["lola"][collection.id]["data_ids"][windowsize][
            assoc.binsize
        ] = str(assoc.id)


def add_embedding_data_to_preprocessed_dataset_map(
    embedding_interval_datasets, output_object, request_context
):
    for embed in embedding_interval_datasets:
        if embed.value_type == "2d-embedding":
            _add_embedding_data_2d_to_preprocessed_dataset_map(embed, output_object, request_context)
        else:
            _add_embedding_data_1d_to_preprocessed_dataset_map(embed, output_object, request_context)


def _add_embedding_data_1d_to_preprocessed_dataset_map(embedding_ds, output_object, request_context):
    """adds embedding interval data for 1d dataset to preprocesse dataset map"""
    collection = Collection.query.get(embedding_ds.collection_id)
    # check whether collection is owned
    if collection.is_access_denied(request_context):
        return
    # check whether there are any uncompleted tasks for the feature dataset
    interval = Intervals.query.get(embedding_ds.intervals_id)
    region_dataset = interval.source_dataset
    # check whether region_dataset is interval
    if region_dataset.sizeType == "Interval":
        windowsize = "variable"
    else:
        windowsize = interval.windowsize
    if (collection in region_dataset.processing_collections) or (
        collection in region_dataset.failed_collections
    ):
        return

    output_object["embedding1d"][collection.id]["name"] = collection.name
    output_object["embedding1d"][collection.id][
        "collection_dataset_names"
    ] = collection.to_json()["dataset_names"]
    output_object["embedding1d"][collection.id]["data_ids"][windowsize][
        embedding_ds.binsize
    ] = str(embedding_ds.id)


def _add_embedding_data_2d_to_preprocessed_dataset_map(embedding_ds, output_object, request_context):
    """adds embedding interval data for 1d dataset to preprocesse dataset map"""
    dataset = Dataset.query.get(embedding_ds.dataset_id)
    # check whether collection is owned
    if dataset.is_access_denied(request_context):
        return
    # check whether there are any uncompleted tasks for the feature dataset
    interval = Intervals.query.get(embedding_ds.intervals_id)
    region_dataset = interval.source_dataset
    # check whether region_dataset is interval
    if region_dataset.sizeType == "Interval":
        windowsize = "variable"
    else:
        windowsize = interval.windowsize
    if (dataset in region_dataset.processing_features) or (
        dataset in region_dataset.failed_features
    ):
        return
    output_object["embedding2d"][dataset.id]["name"] = dataset.dataset_name
    output_object["embedding2d"][dataset.id]["data_ids"][windowsize][
        embedding_ds.binsize
    ][embedding_ds.normalization][embedding_ds.cluster_number] = str(embedding_ds.id)


def recDict():
    """Recursive defaultdict that allows deep
    assignment. recDict[0][1][2] will
    create all intermediate dictionaries."""
    return defaultdict(recDict)


def get_optimal_binsize(regions, target_bin_number):
    """given a dataframe of regions defined via (chrom, start, end) and a
    target bin number, decide which binsize to use for variable size pileup/enrichment analysis"""
    MAX_CHUNK_NUMBER = 250
    sizes = regions["end"] - regions["start"]
    max_size = np.percentile(sizes, 80)
    median_size = np.median(sizes)
    binsizes = sorted(
        [
            int(entry)
            for entry in parse_binsizes(current_app.config["PREPROCESSING_MAP"], "cooler")
        ]
    )
    chunk_number = [max_size / binsize for binsize in binsizes]
    # check if first chunk_number is below 1 -> should indicate error
    if chunk_number[0] <= 1:
        return None
    # flag binsizes that are below max chunk_number
    good_binsizes = [
        (binsize, median_size / binsize)
        for index, binsize in enumerate(binsizes)
        if chunk_number[index] < MAX_CHUNK_NUMBER
    ]
    # check if any retained
    if len(good_binsizes) == 0:
        return None
    # check which binsize is closest to the target binnumber for the mean size
    best_binsize = min(good_binsizes, key=lambda x: abs(x[1] - target_bin_number))
    # return smallest one that is ok
    return best_binsize[0]


def flatten_and_clean_array(array):
    """takes numpy array and converts it to a list where
    numpy.na and +\- np.inf is convert to python None"""
    return [
        entry if not (np.isnan(entry) or np.isinf(entry)) else None
        for entry in array.flatten()
    ]