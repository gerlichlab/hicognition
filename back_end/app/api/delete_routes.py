"""DELETE API endpoints for hicognition"""
from flask.json import jsonify
from flask import g
from .helpers import is_dataset_deletion_denied, remove_safely
from . import api
from .. import db
from ..models import (
    BedFileMetadata,
    Intervals,
    Dataset,
    AverageIntervalData,
    IndividualIntervalData,
    Session
)
from .authentication import auth
from .errors import forbidden, invalid, not_found


@api.route("/datasets/<dataset_id>/", methods=["DELETE"])
@auth.login_required
def delete_dataset(dataset_id):
    """Deletes """
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
    intervals = []
    averageIntervalData = []
    individualIntervalData = []
    metadata = []
    # cooler only needs deletion of derived averageIntervalData
    if dataset.filetype == "cooler":
        averageIntervalData = AverageIntervalData.query.filter(
            AverageIntervalData.dataset_id == dataset_id
        ).all()
    # bedfile needs deletion of intervals and averageIntervalData
    if dataset.filetype == "bedfile":
        intervals = Intervals.query.filter(Intervals.dataset_id == dataset_id).all()
        averageIntervalData = AverageIntervalData.query.filter(
            AverageIntervalData.intervals_id.in_([entry.id for entry in intervals])
        ).all()
        individualIntervalData = IndividualIntervalData.query.filter(
            IndividualIntervalData.intervals_id.in_([entry.id for entry in intervals])
        ).all()
        metadata = BedFileMetadata.query.filter(
            BedFileMetadata.dataset_id == dataset_id
        ).all()
    if dataset.filetype == "bigwig":
        averageIntervalData = AverageIntervalData.query.filter(
            AverageIntervalData.dataset_id == dataset_id
        ).all()
        individualIntervalData = IndividualIntervalData.query.filter(
            IndividualIntervalData.dataset_id == dataset_id
        ).all()
    # get all associated sessions
    sessions = Session.query.filter(Session.datasets.any(id=dataset.id)).all()
    # delete files and remove from database
    deletion_queue = (
        [dataset] + intervals + averageIntervalData + individualIntervalData + metadata + sessions
    )
    for entry in deletion_queue:
        if isinstance(entry, IndividualIntervalData):
            remove_safely(entry.file_path_small)
        if hasattr(entry, "file_path") and (entry.file_path is not None):
            remove_safely(entry.file_path)
        if hasattr(entry, "file_path_sub_sample_index") and (entry.file_path_sub_sample_index is not None):
            remove_safely(entry.file_path_sub_sample_index)
        db.session.delete(
            entry
        )  # TODO: this leaves the session invalid for a short time for some reason -> fix!
    db.session.commit()
    response = jsonify({"message": "success"})
    response.status_code = 200
    return response

@api.route("/sessions/<session_id>/", methods=["DELETE"])
@auth.login_required
def delete_session(session_id):
    """Deletes """
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