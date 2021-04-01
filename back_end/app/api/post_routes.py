"""API endpoints for hicognition"""
import os
import json
import pandas as pd
import numpy as np
from flask.json import jsonify
from werkzeug.utils import secure_filename
from flask import g, request, current_app
from . import api
from .. import db
from ..models import Dataset, BedFileMetadata
from .authentication import auth
from .helpers import is_access_to_dataset_denied, parse_description_and_genotype
from .format_checkers import FORMAT_CHECKERS
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
        # check format
        if not FORMAT_CHECKERS[request.form["filetype"]](request.files["file"]):
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
    # save file in upload directory with database_id as prefix
    filename = f"{new_entry.id}_{secure_filename(fileObject.filename)}"
    file_path = os.path.join(current_app.config["UPLOAD_DIR"], filename)
    fileObject.save(file_path)
    # add file_path to database entry
    new_entry.file_path = file_path
    new_entry.processing_state = "uploaded"
    db.session.add(new_entry)
    # start preprocessing of bedfile, the other filetypes do not need preprocessing
    if data["filetype"] == "bedfile":
        current_user.launch_task("pipeline_bed", "run bed preprocessing", new_entry.id)
        # set processing state
        new_entry.processing_state = "processing"
    db.session.commit()
    return jsonify({"message": "success! Preprocessing triggered."})


@api.route("/preprocess/", methods=["POST"])
@auth.login_required
def preprocess_dataset():
    """Starts preprocessing pipeline
    for datasets specified in the request body"""
    # TODO: Reset processing state of job -> delete all tasks that are in progress when new submission

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
        return forbidden(f"Dataset is not owned by logged in user!")
    if Dataset.query.get(dataset_id).filetype == "cooler":
        current_user.launch_task(
            "pipeline_pileup",
            "run pileup pipeline",
            dataset_id,
            binsizes,
            interval_ids,
        )
    if Dataset.query.get(dataset_id).filetype == "bigwig":
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


@api.route("/bedFileMetadata/", methods=["POST"])
@auth.login_required
def add_bedfile_metadata():
    """Add metadata file to metadata table.
    If uploaded metadatafile has different row-number than original bedfile ->
    return error."""

    SEPARATOR_MAP = {",": ",", ";": ";", "tab": "\t"}

    def is_form_invalid():
        if not hasattr(request, "form"):
            return True
        # check attributes
        if "datasetID" not in request.form.keys():
            return True
        if "separator" not in request.form.keys():
            return True
        # check whether fileObject is there
        if len(request.files) == 0:
            return True
        # check filename
        fileEnding = request.files["file"].filename.split(".")[-1]
        correctFileEndings = ["csv", "txt", "bed"]  # textfiles and bedfiles supported
        if fileEnding not in correctFileEndings:
            return True
        return False

    # check form
    if is_form_invalid():
        return invalid("Form is not valid!")
    # get data from form
    data = request.form
    fileObject = request.files["file"]
    dataset_id = json.loads(data["datasetID"])
    # check whether dataset exists and user is allowed to access
    if Dataset.query.get(dataset_id) is None:
        return not_found("Dataset does not exist!")
    if is_access_to_dataset_denied(Dataset.query.get(dataset_id), g.current_user):
        return forbidden(f"Dataset is not owned by logged in user!")
    # check whether row-number is correct
    dataset = Dataset.query.get(dataset_id)
    dataset_file = pd.read_csv(
        dataset.file_path, sep="\t", header=None
    )  # during upload process, the header of bedfiles is removed
    uploaded_file = pd.read_csv(
        fileObject, sep=SEPARATOR_MAP[data["separator"]]
    )  # generate uploaded dataframe from io-stream in memory
    if len(dataset_file) != len(uploaded_file):
        return jsonify({"ValidationError": "Dataset length missmatch!"})
    # detect numeric columns
    only_numeric = uploaded_file.select_dtypes(include=np.number)
    # save with standard separator
    filename = secure_filename(fileObject.filename)
    file_path = os.path.join(current_app.config["UPLOAD_DIR"], filename)
    only_numeric.to_csv(file_path, index=False)
    # add to database
    new_metadata = BedFileMetadata(
        name=file_path.split(os.sep)[-1], file_path=file_path, dataset_id=dataset_id
    )
    db.session.add(new_metadata)
    db.session.commit()
    # return field_names to include for metadata
    return jsonify(
        {
            "message": "success! Preprocessing triggered.",
            "field_names": list(sorted(only_numeric.columns)),
            "id": new_metadata.id,
        }
    )


@api.route("/bedFileMetadata/<metadata_id>/setFields", methods=["POST"])
@auth.login_required
def add_bedfile_metadata_fields(metadata_id):
    """Add relevant metadatafields of the corresponding metadatafile."""

    def is_form_invalid():
        if not hasattr(request, "form"):
            return True
        # check attributes
        if "fields" not in request.form.keys():
            return True
        return False

    # check form
    if is_form_invalid():
        return invalid("Form is not valid!")
    # get data from form
    data = request.form
    field_map = json.loads(data["fields"])
    # check whether dataset exists and user is allowed to access
    if BedFileMetadata.query.get(metadata_id) is None:
        return not_found("Metadataset does not exist!")
    if is_access_to_dataset_denied(
        BedFileMetadata.query.get(metadata_id).associated_dataset, g.current_user
    ):
        return forbidden(f"Associated dataset is not owned by logged in user!")
    # check whether field_names are correct
    metadata = BedFileMetadata.query.get(metadata_id)
    metadata_file = pd.read_csv(metadata.file_path)
    if not all(key in metadata_file.columns for key in field_map):
        return invalid("Field names not understood!")
    # store field_map in database
    metadata.metadata_fields = json.dumps(field_map)
    db.session.commit()
    return jsonify({"message": "Success! Field map added."})
