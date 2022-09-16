"""API endpoints for hicognition"""
from flask import g, request
from flask.json import jsonify
from . import api
from .. import db
from ..models import Dataset
from .authentication import auth
from .errors import forbidden, invalid, not_found


@api.route("/datasets/<dataset_id>/", methods=["PUT"])
@auth.login_required
def modify_dataset(dataset_id):
    """endpoint to add a new dataset"""

    def is_form_invalid(filetype):
        if not hasattr(request, "form"):
            return True
        # check attributes
        if not Dataset.modify_dataset_requirements_fulfilled(request.form, filetype):
            return True
        return False

    # check whether dataset exists
    dataset = Dataset.query.get(dataset_id)
    # check whether dataset exists
    if dataset is None:
        return not_found(f"Dataset with id '{dataset_id}' does not exist!")
    # check whether user owns the dataset
    if dataset.is_access_denied(g):
        return forbidden(
            f"Dataset with id '{dataset_id}' is not owned by logged in user!"
        )
    # check form
    if is_form_invalid(dataset.filetype):
        return invalid("Form is not valid!")
    # get data from form
    data = request.form
    # blank metadata fields
    dataset.blank_fields()
    dataset.add_fields_from_form(
        data, requirement_spec=Dataset.DATASET_META_FIELDS_MODIFY
    )
    db.session.add(dataset)
    db.session.commit()
    return jsonify({"message": "success! Preprocessing triggered."})


@api.route("/user/<id>", methods=["POST"])
@auth.login_required
def modify_user(user_id):
    # which side should i start implementing from?
    # 1. model
    # 2. here
    # 3. front
    pass