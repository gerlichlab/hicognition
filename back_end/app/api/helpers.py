"""Helper functions for api routes"""

def is_access_to_dataset_denied(dataset_id, current_user):
    """Checks whether access to a certian dataset is denied
    for a given user."""
    return (dataset_id.user_id != current_user.id) and not dataset_id.public

def is_dataset_deletion_denied(dataset_id, current_user):
    """Checks whether access to a certian dataset is denied
    for a given user."""
    return (dataset_id.user_id != current_user.id)


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