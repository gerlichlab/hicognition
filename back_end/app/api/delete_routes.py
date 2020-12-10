"""DELETE API endpoints for hicognition"""
import pandas as pd
from flask.json import jsonify
from flask import g, request
from .helpers import update_processing_state, is_access_to_dataset_denied
from . import api
from .. import db
from ..models import Pileupregion, Dataset, Pileup
from .authentication import auth

@api.route("/datasets/<dataset_id>/", methods=["DELETE"])
@auth.login_required
def delete_dataset(dataset_id):
    """Deletes """
    # check if data set exists
    dataset = Dataset.query.get(dataset_id)
    if dataset is None:
        response = jsonify({"error": f"Dataset id {dataset_id} does not exist!"})
        response.status_code = 404
        return response
    # check if data set can be accessed
    if is_access_to_dataset_denied(dataset, g.current_user):
        response = jsonify({"error": f"Dataset id {dataset_id} is not owned!"})
        response.status_code = 401
        return response
    response = jsonify({"message": "success"})
    response.status_code = 200
    return response