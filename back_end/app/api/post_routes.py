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
from .helpers import is_access_to_dataset_denied, parse_description_and_genotype
from .errors import forbidden, invalid, not_found


@api.route("/datasets/", methods=["POST"])
@auth.login_required
def add_dataset():
    """endpoint to add a new dataset"""

    def is_form_invalid():
        if not hasattr(request, "form"):
            return True
        # check attributes
        if "datasetName" not in request.form.keys():
            return True
        if "filetype" not in request.form.keys():
            return True
        # check whether fileObject is there
        if len(request.files) == 0:
            return True
        # check filename
        fileEnding = request.files["file"].filename.split(".")[-1]
        correctFileEndings = {"bedfile": "bed", "cooler": "mcool", "bigwig": "bw"}
        if request.form["filetype"] not in correctFileEndings:
            return True
        if correctFileEndings[request.form["filetype"]] != fileEnding:
            return True
        return False


    current_user = g.current_user
    # check form
    if is_form_invalid():
        return invalid("Form is not valid!")
    # get data from form
    data = request.form
    fileObject = request.files["file"]
    # check whether description and genotype is there
    description, genotype = parse_description_and_genotype(data)
    # check whether dataset should be public
    setPublic = False
    if "public" in data:
        if data["public"].lower() == "true":
            setPublic = True
    # add data to Database -> in order to show uploading
    new_entry = Dataset(
        dataset_name=data["datasetName"],
        genotype=genotype,
        description=description,
        public=setPublic,
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
    if data["filetype"] not in ["cooler", "bedfile", "bigwig"]:
        return invalid("datatype not understood")
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
    elif data["filetype"] == "cooler":
        current_user.launch_task(
            "pipeline_cooler", "run cooler preprocessing", new_entry.id
        )
        # cooler files stay at processing status upload for the initial higlass addition pipeline
        db.session.commit()
    else:
        current_user.launch_task(
            "pipeline_bigwig", "run bigwig preprocessing", new_entry.id
        )
        # bigwig files stay at processing status upload for the initial higlass addition pipeline
        db.session.commit()
    return jsonify({"message": "success! Preprocessing triggered."})


@api.route("/preprocess/", methods=["POST"])
@auth.login_required
def preprocess_dataset():
    """Starts preprocessing pipeline
    for datasets specified in the request body"""
    #TODO: Reset processing state of job -> delete all tasks that are in progress when new submission

    def is_form_invalid():
        if not hasattr(request, "form"):
            return True
        if sorted(list(request.form.keys())) != sorted(
            ["dataset_id", "binsizes", "interval_ids"]
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
    interval_ids = json.loads(data["interval_ids"])
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
        interval_ids,
    )
    # set processing state
    dataset = Dataset.query.get(dataset_id)
    dataset.processing_state = "processing"
    db.session.commit()
    return jsonify({"message": "success! Preprocessing triggered."})

@api.route("/preprocessbigwig/", methods=["POST"])
#TODO: post this on main preprocessroute
@auth.login_required
def preprocess_bigwig_dataset():
    """Starts preprocessing pipeline
    for datasets specified in the request body"""
    #TODO: Reset processing state of job -> delete all tasks that are in progress when new submission

    def is_form_invalid():
        if not hasattr(request, "form"):
            return True
        if sorted(list(request.form.keys())) != sorted(
            ["dataset_id", "binsizes", "interval_ids"]
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
    interval_ids = json.loads(data["interval_ids"])
    # check whether dataset exists
    if Dataset.query.get(dataset_id) is None:
        return not_found("Dataset does not exist!")
    if is_access_to_dataset_denied(Dataset.query.get(dataset_id), g.current_user):
        return forbidden(f"Cooler dataset is not owned by logged in user!")
    current_user.launch_task(
        "pipeline_stackup",
        "run stackup pipeline",
        dataset_id,
        binsizes,
        interval_ids,
    )
    # set processing state
    dataset = Dataset.query.get(dataset_id)
    dataset.processing_state = "processing"
    db.session.commit()
    return jsonify({"message": "success! Preprocessing triggered."})
