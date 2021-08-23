"""DELETE API endpoints for hicognition"""
from flask.json import jsonify
from flask import g
from .helpers import is_dataset_deletion_denied, delete_collection, delete_dataset
from . import api
from .. import db
from ..models import (
    BedFileMetadata,
    Collection,
    Intervals,
    Dataset,
    AverageIntervalData,
    IndividualIntervalData,
    Session,
    dataset_collection_assoc_table,
)
from .authentication import auth
from .errors import forbidden, invalid, not_found


@api.route("/datasets/<dataset_id>/", methods=["DELETE"])
@auth.login_required
def delete_dataset_handler(dataset_id):
    """Deletes"""
    # check if data set exists
    dataset = Dataset.query.get(dataset_id)
    if dataset is None:
        return not_found(f"Dataset id {dataset_id} does not exist!")
    # check if data set can be accessed
    if is_dataset_deletion_denied(dataset, g.current_user):
        return forbidden(f"Dataset with id {dataset_id} is not owned by user!")
    # check if data set is processing
    if dataset.processing_state == "processing":
        return invalid(f"Dataset is in processing state!")
    # delete dataset
    delete_dataset(dataset, db)
    # delete associated collections
    collections = [
        Collection.query.get(ds.collection_id)
        for ds in db.session.query(dataset_collection_assoc_table).filter_by(
            dataset_id=dataset.id
        ).all()
    ]
    for collection in collections:
        delete_collection(collection, db)
    db.session.commit()
    response = jsonify({"message": "success"})
    response.status_code = 200
    return response


@api.route("/sessions/<session_id>/", methods=["DELETE"])
@auth.login_required
def delete_session_handler(session_id):
    """Deletes Session."""
    # check if data set exists
    session = Session.query.get(session_id)
    if session is None:
        return not_found(f"Session with id {session_id} does not exist!")
    # check if data set can be accessed
    if session.user_id != g.current_user.id:
        return forbidden(f"Session with id {session_id} is not owned by user!")
    # delete session
    db.session.delete(session)
    db.session.commit()
    response = jsonify({"message": "success"})
    response.status_code = 200
    return response


@api.route("/collections/<collection_id>/", methods=["DELETE"])
@auth.login_required
def delete_collection_handler(collection_id):
    """Deletes Collection."""
    # TODO: delete everything associated!
    # check if data set exists
    collection = Collection.query.get(collection_id)
    if collection is None:
        return not_found(f"Collection with id {collection_id} does not exist!")
    # check if data set can be accessed
    if collection.user_id != g.current_user.id:
        return forbidden(f"Collection with id {collection_id} is not owned by user!")
    # delete session
    delete_collection(collection, db)
    db.session.commit()
    response = jsonify({"message": "success"})
    response.status_code = 200
    return response
