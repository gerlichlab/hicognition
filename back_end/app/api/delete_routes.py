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
    response = jsonify({"error": "Not implemented"})
    response.status_code = 500
    return response