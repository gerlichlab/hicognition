"""Helper functions for api routes"""
import os
from .. import db
from collections import defaultdict
from flask import current_app
from ..models import (
    Intervals,
    Dataset,
    Collection,
    Task,
    IndividualIntervalData,
    AverageIntervalData,
    Session,
    BedFileMetadata,
    session_collection_assoc_table,
)


def is_access_to_dataset_denied(dataset, g):
    """Checks whether access to a certian dataset is denied
    for a given user."""
    if dataset.public:
        return False
    if (dataset.user_id != g.current_user.id) and (
        dataset.id not in g.session_datasets
    ):
        return True
    return False


def is_access_to_collection_denied(collection, g):
    """Checks whether access to a certian dataset is denied
    for a given user."""
    if collection.public:
        return False
    if (collection.user_id != g.current_user.id) and (
        collection.id not in g.session_collections
    ):
        return True
    return False


def is_dataset_deletion_denied(dataset_id, current_user):
    """Checks whether access to a certian dataset is denied
    for a given user."""
    return dataset_id.user_id != current_user.id


def update_processing_state(entries, db):
    """updates processing state of all entries (must implement set_processing_state) in the supplied iterable"""
    for entry in entries:
        entry.set_processing_state(db)


def parse_description_and_genotype(form_data):
    if ("genotype" not in form_data) or (form_data["genotype"] == "null"):
        genotype = "No genotype provided"
    else:
        genotype = form_data["genotype"]
    if ("description" not in form_data) or (form_data["description"] == "null"):
        description = "No description provided"
    else:
        description = form_data["description"]
    return description, genotype


def delete_collection(collection, db):
    """deletes collection and associated data."""
    assoc_data = collection.associationData.all()
    embed_data = collection.embeddingData.all()
    deletion_queue = assoc_data + embed_data
    for entry in deletion_queue:
        # remove files
        remove_safely(entry.file_path)
        if hasattr(entry, "file_path_feature_values"):
            remove_safely(entry.file_path_feature_values)
    db.session.delete(collection)


def delete_associated_data_of_dataset(dataset):
    """deletes associated data of database entries. Actual deletion of entries
    is handeled by database cascades"""
    intervals = []
    averageIntervalData = []
    individualIntervalData = []
    metadata = []
    # cooler only needs deletion of derived averageIntervalData
    if dataset.filetype == "cooler":
        averageIntervalData = AverageIntervalData.query.filter(
            AverageIntervalData.dataset_id == dataset.id
        ).all()
    # bedfile needs deletion of intervals and averageIntervalData
    if dataset.filetype == "bedfile":
        intervals = Intervals.query.filter(Intervals.dataset_id == dataset.id).all()
        averageIntervalData = AverageIntervalData.query.filter(
            AverageIntervalData.intervals_id.in_([entry.id for entry in intervals])
        ).all()
        individualIntervalData = IndividualIntervalData.query.filter(
            IndividualIntervalData.intervals_id.in_([entry.id for entry in intervals])
        ).all()
        metadata = BedFileMetadata.query.filter(
            BedFileMetadata.dataset_id == dataset.id
        ).all()
    if dataset.filetype == "bigwig":
        averageIntervalData = AverageIntervalData.query.filter(
            AverageIntervalData.dataset_id == dataset.id
        ).all()
        individualIntervalData = IndividualIntervalData.query.filter(
            IndividualIntervalData.dataset_id == dataset.id
        ).all()
    # delete files and remove from database
    deletion_queue = [dataset] + intervals + averageIntervalData + individualIntervalData + metadata
    for entry in deletion_queue:
        if isinstance(entry, IndividualIntervalData):
            remove_safely(entry.file_path_small)
        if hasattr(entry, "file_path") and (entry.file_path is not None):
            remove_safely(entry.file_path)
        if hasattr(entry, "file_path_sub_sample_index") and (
            entry.file_path_sub_sample_index is not None
        ):
            remove_safely(entry.file_path_sub_sample_index)


def remove_safely(file_path):
    """Tries to remove a file and logs warning with app logger if this does not work."""
    try:
        os.remove(file_path)
    except BaseException:
        current_app.logger.warning(
            f"Tried removing {file_path}, but file does not exist!"
        )


def remove_failed_tasks(tasks, db):
    for task in tasks:
        if task.get_rq_job() is None:
            continue
        if task.get_rq_job().get_status() == "failed":
            db.session.delete(task)
    db.session.commit()


def get_all_interval_ids(region_datasets):
    """Returns ids of all intervals associated with list or region datasets."""
    interval_ids = []
    for region_dataset in region_datasets:
        interval_ids.extend([entry.id for entry in region_dataset.intervals.all()])
    return interval_ids


def parse_binsizes(map):
    """returns needed binsizes from preprocessing map."""
    binsizes = set()
    for windowsize, bins in map.items():
        binsizes |= set(bins)
    return list(binsizes)


def add_average_data_to_preprocessed_dataset_map(
    average_interval_datasets, output_object, request_context
):
    for average in average_interval_datasets:
        dataset = Dataset.query.get(average.dataset_id)
        # check whether dataset is owned
        if is_access_to_dataset_denied(dataset, request_context):
            continue
        # check whether there are any uncompleted tasks for the region dataset associated with these features
        interval = Intervals.query.get(average.intervals_id)
        region_dataset = interval.source_dataset
        tasks_on_interval = (
            Task.query.join(Intervals)
            .join(Dataset)
            .filter((Task.dataset_id == dataset.id) & (Dataset.id == region_dataset.id))
            .all()
        )
        if len(tasks_on_interval) != 0 and any(
            not task.complete for task in tasks_on_interval
        ):
            continue
        if average.value_type in ["Obs/Exp", "ICCF"]:
            output_object["pileup"][dataset.id]["name"] = dataset.dataset_name
            output_object["pileup"][dataset.id]["data_ids"][interval.windowsize][
                average.binsize
            ][average.value_type] = str(average.id)
        else:
            output_object["lineprofile"][dataset.id]["name"] = dataset.dataset_name
            output_object["lineprofile"][dataset.id]["data_ids"][interval.windowsize][
                average.binsize
            ] = str(average.id)


def add_individual_data_to_preprocessed_dataset_map(
    individual_interval_datasets, output_object, request_context
):
    for individual in individual_interval_datasets:
        dataset = Dataset.query.get(individual.dataset_id)
        # check whether dataset is owned
        if is_access_to_dataset_denied(dataset, request_context):
            continue
        # check whether there are any uncompleted tasks for the feature dataset
        interval = Intervals.query.get(individual.intervals_id)
        region_dataset = interval.source_dataset
        tasks_on_interval = (
            Task.query.join(Intervals)
            .join(Dataset)
            .filter((Task.dataset_id == dataset.id) & (Dataset.id == region_dataset.id))
            .all()
        )
        if len(tasks_on_interval) != 0 and any(
            not task.complete for task in tasks_on_interval
        ):
            continue
        output_object["stackup"][dataset.id]["name"] = dataset.dataset_name
        output_object["stackup"][dataset.id]["data_ids"][interval.windowsize][
            individual.binsize
        ] = str(individual.id)


def add_association_data_to_preprocessed_dataset_map(
    association_interval_datasets, output_object, request_context
):
    for assoc in association_interval_datasets:
        collection = Collection.query.get(assoc.collection_id)
        # check whether collection is owned
        if is_access_to_collection_denied(collection, request_context):
            continue
        # check whether there are any uncompleted tasks for the feature dataset
        interval = Intervals.query.get(assoc.intervals_id)
        region_dataset = interval.source_dataset
        tasks_on_interval = (
            Task.query.join(Intervals)
            .join(Dataset)
            .filter(
                (Task.collection_id == collection.id)
                & (Dataset.id == region_dataset.id)
            )
            .all()
        )
        if len(tasks_on_interval) != 0 and any(
            not task.complete for task in tasks_on_interval
        ):
            continue
        output_object["lola"][collection.id]["name"] = collection.name
        output_object["lola"][collection.id][
            "collection_dataset_names"
        ] = collection.to_json()["dataset_names"]
        output_object["lola"][collection.id]["data_ids"][interval.windowsize][
            assoc.binsize
        ] = str(assoc.id)


def add_embedding_data_to_preprocessed_dataset_map(
    embedding_interval_datasets, output_object, request_context
):
    for embed in embedding_interval_datasets:
        collection = Collection.query.get(embed.collection_id)
        # check whether collection is owned
        if is_access_to_collection_denied(collection, request_context):
            continue
        # check whether there are any uncompleted tasks for the feature dataset
        interval = Intervals.query.get(embed.intervals_id)
        region_dataset = interval.source_dataset
        tasks_on_interval = (
            Task.query.join(Intervals)
            .join(Dataset)
            .filter(
                (Task.collection_id == collection.id)
                & (Dataset.id == region_dataset.id)
            )
            .all()
        )
        if len(tasks_on_interval) != 0 and any(
            not task.complete for task in tasks_on_interval
        ):
            continue
        output_object["embedding"][collection.id]["name"] = collection.name
        output_object["embedding"][collection.id][
            "collection_dataset_names"
        ] = collection.to_json()["dataset_names"]
        output_object["embedding"][collection.id]["data_ids"][interval.windowsize][
            embed.binsize
        ] = str(embed.id)


def recDict():
    """Recursive defaultdict that allows deep
    assignment. recDict[0][1][2] will
    create all intermediate dictionaries."""
    return defaultdict(recDict)
