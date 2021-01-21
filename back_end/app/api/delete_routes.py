"""DELETE API endpoints for hicognition"""
import os
from flask.json import jsonify
from flask import g, current_app
from .helpers import is_access_to_dataset_denied
from . import api
from .. import db
from ..models import Intervals, Dataset, AverageIntervalData
from .authentication import auth
from .errors import forbidden, not_found



@api.route("/datasets/<dataset_id>/", methods=["DELETE"])
@auth.login_required
def delete_dataset(dataset_id):
    """Deletes """
    # check if data set exists
    dataset = Dataset.query.get(dataset_id)
    if dataset is None:
        return not_found(f"Dataset id {dataset_id} does not exist!")
    # check if data set can be accessed
    if is_access_to_dataset_denied(dataset, g.current_user):
        return forbidden(f"Dataset with id {dataset_id} is not owned by user!")
    # check if data set is processing
    if dataset.processing_state == "processing":
        return forbidden(f"Dataset is in processing state!")
    # cooler only needs deletion of derived averageIntervalData
    intervals = []
    averageIntervalData = []
    if dataset.filetype == "cooler":
        averageIntervalData = AverageIntervalData.query.filter(AverageIntervalData.cooler_id == dataset_id).all()
    # bedfile needs deletion of intervals and averageIntervalData
    if dataset.filetype == "bedfile":
        intervals = Intervals.query.filter(Intervals.dataset_id == dataset_id).all()
        averageIntervalData = AverageIntervalData.query.filter(AverageIntervalData.intervals_id.in_([entry.id for entry in intervals])).all()
    # delete files and remove from database
    deletion_queue = [dataset] + intervals + averageIntervalData
    for entry in deletion_queue:
        try:
            if entry.file_path is not None:
                os.remove(entry.file_path)
            else:
                current_app.logger.warning(f"Tried removing {entry.file_path}, but there was no filepath!")
        except FileNotFoundError:
            current_app.logger.warning(f"Tried removing {entry.file_path}, but file does not exist!")
        db.session.delete(entry) # TODO: this leaves the session invalid for a short time for some reason -> fix!
    db.session.commit()
    response = jsonify({"message": "success"})
    response.status_code = 200
    return response
