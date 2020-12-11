"""API endpoints for hicognition"""
import os
import json
from flask.json import jsonify
from werkzeug.utils import secure_filename
from flask import g, request, current_app
from . import api
from .. import db
from ..models import Dataset
from .authentication import auth
from .helpers import is_access_to_dataset_denied
from .errors import forbidden, invalid, not_found


@api.route("/datasets/", methods=["POST"])
@auth.login_required
def add_dataset():
    """endpoint to add a new dataset"""
    current_user = g.current_user
    # get data from form
    
    data = request.form
    fileObject = request.files["file"]
    # add data to Database -> in order to show uploading
    new_entry = Dataset(
        dataset_name=data["datasetName"],
        genotype=data.get("genotype", "undefined"),
        description=data.get("description", "undefined"),
        processing_state="uploading",
        filetype=data["filetype"],
        user_id=current_user.id,
    )
    db.session.add(new_entry)
    db.session.commit()
    # save file in upload directory
    filename = secure_filename(fileObject.filename)
    file_path = os.path.join(current_app.config["UPLOAD_DIR"], filename)
    fileObject.save(file_path)
    if data["filetype"] not in ["cooler", "bedfile"]:
        return forbidden("datatype not understood")
    # add file_path to database entr
    new_entry.file_path = file_path
    new_entry.processing_state = "uploaded"
    db.session.add(new_entry)
    db.session.commit()
    # start preprocessing
    if data["filetype"] == "bedfile":
        current_user.launch_task("pipeline_bed", "run bed preprocessing", new_entry.id)
        # set processing state
        new_entry.processing_state = "processing"
        db.session.commit()
    else:
        current_user.launch_task(
            "pipeline_cooler", "run cooler preprocessing", new_entry.id
        )
        # cooler files stay at processing status upload for the initial higlass addition pipeline
        db.session.commit()
    return jsonify({"message": "success! Preprocessing triggered."})


@api.route("/preprocess/", methods=["POST"])
@auth.login_required
def preprocess_dataset():
    """Starts preprocessing pipeline
    for datasets specified in the request body"""

    def is_form_invalid():
        if not hasattr(request, "form"):
            return True
        if sorted(list(request.form.keys())) != sorted(
            ["dataset_id", "binsizes", "pileup_region_ids"]
        ):
            return True
        return False

    current_user = g.current_user
    # check form
    if is_form_invalid():
        return invalid("Form is not valid!")
    # get data from form
    data = request.form
    dataset_id = json.loads(data["dataset_id"])
    binsizes = json.loads(data["binsizes"])
    pileup_region_ids = json.loads(data["pileup_region_ids"])
    # check whether dataset exists
    if Dataset.query.get(dataset_id) is None:
        return not_found("Dataset does not exist!")
    if is_access_to_dataset_denied(Dataset.query.get(dataset_id), g.current_user):
        return forbidden(f"Cooler dataset is not owned by logged in user!")
    current_user.launch_task(
        "pipeline_pileup",
        "run pileup pipeline",
        dataset_id,
        binsizes,
        pileup_region_ids,
    )
    # set processing state
    dataset = Dataset.query.get(dataset_id)
    dataset.processing_state = "processing"
    db.session.commit()
    return jsonify({"message": "success! Preprocessing triggered."})
