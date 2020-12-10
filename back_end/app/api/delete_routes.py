"""DELETE API endpoints for hicognition"""
import os
from flask.json import jsonify
from flask import g
from .helpers import is_access_to_dataset_denied
from . import api
from .. import db
from ..models import Pileupregion, Dataset, Pileup
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
    # cooler only needs deletion of derived pileups
    pileup_regions = []
    pileups = []
    if dataset.filetype == "cooler":
        pileups = Pileup.query.filter(Pileup.cooler_id == dataset_id).all()
    # bedfile needs deletion of pileupregions and pileups
    if dataset.filetype == "bedfile":
        pileup_regions = Pileupregion.query.filter(Pileupregion.dataset_id == dataset_id).all()
        pileups = Pileup.query.filter(Pileup.pileupregion_id.in_([entry.id for entry in pileup_regions])).all()
    # delete files and remove from database
    deletion_queue = [dataset] + pileup_regions + pileups
    for entry in deletion_queue:
        if os.path.exists(entry.file_path):
            os.remove(entry.file_path)
        db.session.delete(entry)
    db.session.commit()
    response = jsonify({"message": "success"})
    response.status_code = 200
    return response
