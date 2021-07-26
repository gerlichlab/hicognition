"""Helper functions for api routes"""
import os
from collections import defaultdict
from flask import current_app
from ..models import Intervals, Dataset


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


def update_processing_state(datasets, db):
    """updates processing state of all datasets in the supplied iterable"""
    for dataset in datasets:
        dataset.set_processing_state(db)


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
        interval = Intervals.query.get(average.intervals_id)
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
        interval = Intervals.query.get(individual.intervals_id)
        output_object["stackup"][dataset.id]["name"] = dataset.dataset_name
        output_object["stackup"][dataset.id]["data_ids"][interval.windowsize][
            individual.binsize
        ] = str(individual.id)


def recDict():
    """Recursive defaultdict that allows deep
    assignment. recDict[0][1][2] will
    create all intermediate dictionaries."""
    return defaultdict(recDict)
