"""API endpoints for hicognition"""
import os
import json
import pandas as pd
import cooler
import numpy as np
from flask.json import jsonify
from werkzeug.utils import secure_filename
from flask import g, request, current_app
from . import api
from .. import db
from ..models import (
    Assembly,
    Dataset,
    BedFileMetadata,
    Organism,
    Task,
    Session,
    Intervals,
    Collection,
)
from .authentication import auth
from .helpers import (
    is_access_to_dataset_denied,
    is_access_to_collection_denied,
    parse_description,
    remove_failed_tasks,
    get_all_interval_ids,
    parse_binsizes,
    modify_dataset_requirements_fulfilled,
    blank_dataset,
    add_fields_to_dataset
)
from .errors import forbidden, invalid, not_found
from hicognition.format_checkers import FORMAT_CHECKERS


@api.route("/datasets/<dataset_id>/", methods=["PUT"])
@auth.login_required
def modify_dataset(dataset_id):
    """endpoint to add a new dataset"""

    def is_form_invalid():
        if not hasattr(request, "form"):
            return True
        # check attributes
        if not modify_dataset_requirements_fulfilled(request.form):
            return True
        return False

    # check whether dataset exists
    dataset = Dataset.query.get(dataset_id)
    # check whether dataset exists
    if dataset is None:
        return not_found(f"Dataset with id '{dataset_id}' does not exist!")
    # check whether user owns the dataset
    if is_access_to_dataset_denied(dataset, g):
        return forbidden(
            f"Dataset with id '{dataset_id}' is not owned by logged in user!"
        )
    # check form
    if is_form_invalid():
        return invalid("Form is not valid!")
    # get data from form
    data = request.form
    # blank metadata fields
    blank_dataset(dataset)
    add_fields_to_dataset(dataset, data)
    db.session.add(dataset)
    db.session.commit()
    return jsonify({"message": "success! Preprocessing triggered."})
