"""DELETE API endpoints for hicognition"""
from flask.json import jsonify
from flask import g
from .helpers import is_dataset_deletion_denied, delete_collection, delete_associated_data_of_dataset, remove_safely
from . import api
from .. import db
from ..models import (
    Assembly,
    Collection,
    Dataset,
    Session,
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
    if (len(dataset.processing_features) != 0) or (len(dataset.processing_regions) != 0):
        return invalid(f"Dataset is in processing state!")
    # delete associated data of dataset
    delete_associated_data_of_dataset(dataset)
    # get collections and sessions
    collections = dataset.collections
    sessions = dataset.sessions
    # delete dataset, will trigger all cascades
    db.session.delete(dataset)
    db.session.commit()
    # delete associated collections
    for collection in collections:
        delete_collection(collection, db)
    # delete associated sessions
    for session in sessions:
        db.session.delete(session)
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


@api.route("/assemblies/<assembly_id>/", methods=["DELETE"])
@auth.login_required
def delete_assembly_handler(assembly_id):
    """Deletes assemblies. Assemblies can only be deleted if no datasets are associated.."""
    # check if assembly exists
    assembly = Assembly.query.get(assembly_id)
    if assembly is None:
        return not_found(f"Assembly with id {assembly_id} does not exist!")
    # check if data set can be accessed
    if assembly.user_id != g.current_user.id:
        return forbidden(f"Assembly with id {assembly_id} is not owned by user!")
    # check whether assembly is associated with datasets
    if len(Dataset.query.filter(Dataset.assembly == assembly.id).all()) != 0:
        return forbidden(f"Assembly can only be deleted if it is not associated with any datasets!")
    # delete assembly
    remove_safely(assembly.chrom_sizes)
    remove_safely(assembly.chrom_arms)
    db.session.delete(assembly)
    db.session.commit()
    response = jsonify({"message": "success"})
    response.status_code = 200
    return response
