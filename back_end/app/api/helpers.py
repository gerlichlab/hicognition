"""Helper functions for api routes"""
import os
from flask import current_app


def is_access_to_dataset_denied(dataset, g):
    """Checks whether access to a certian dataset is denied
    for a given user."""
    if dataset.public:
        return False
    if dataset.id in g.session_datasets:
        return False
    return (dataset.user_id != g.current_user.id)


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