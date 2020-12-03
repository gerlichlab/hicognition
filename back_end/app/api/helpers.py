"""Helper functions for api routes"""

def is_access_to_dataset_denied(dataset_id, current_user):
    """Checks whether access to a certian dataset is denied
    for a given user."""
    return dataset_id.user_id != current_user.id


def update_processing_state(datasets, db):
    """updates processing state of all datasets in the supplied iterabel"""
    for dataset in datasets:
        dataset.set_processing_state(db)