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
from ..models import Dataset, BedFileMetadata, Task, Session, Intervals
from .authentication import auth
from .helpers import is_access_to_dataset_denied, parse_description_and_genotype, remove_failed_tasks
from .errors import forbidden, invalid, not_found
from hicognition.format_checkers import FORMAT_CHECKERS


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
        correctFileEndings = {
            "bedfile": ["bed"],
            "cooler": ["mcool"],
            "bigwig": ["bw", "bigwig"],
        }
        if request.form["filetype"] not in correctFileEndings:
            return True
        if fileEnding.lower() not in correctFileEndings[request.form["filetype"]]:
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
    # check format -> this cannot be done in form checker since file needs to be available
    chromosome_names = set(
        pd.read_csv(current_app.config["CHROM_SIZES"], header=None, sep="\t")[0]
    )
    if not FORMAT_CHECKERS[request.form["filetype"]](file_path, chromosome_names):
        # remove entry from database
        db.session.delete(new_entry)
        db.session.commit()
        # remove file
        os.remove(file_path)
        # return error
        return invalid("Wrong dataformat or wrong chromosome names!")
    # add file_path to database entry
    new_entry.file_path = file_path
    new_entry.processing_state = "uploaded"
    db.session.add(new_entry)
    # start preprocessing of bedfile, the other filetypes do not need preprocessing
    if data["filetype"] == "bedfile":
        current_user.launch_task("pipeline_bed", "run bed preprocessing", new_entry.id)
        # set processing state
        new_entry.processing_state = "processing"
    # if filetype is cooler, store available binsizes
    if data["filetype"] == "cooler":
        binsizes = [
            resolution.split("/")[2]
            for resolution in cooler.fileops.list_coolers(file_path)
        ]
        new_entry.available_binsizes = json.dumps(binsizes)
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
    if is_access_to_dataset_denied(Dataset.query.get(dataset_id), g):
        return forbidden(f"Dataset is not owned by logged in user!")
    # delete all jobs that are in database and have failed
    associated_tasks = Task.query.filter_by(dataset=Dataset.query.get(dataset_id)).all()
    remove_failed_tasks(associated_tasks, db)
    # dispatch appropriate pipelines
    if Dataset.query.get(dataset_id).filetype == "cooler":
        
        for binsize in binsizes:
            for interval_id in interval_ids:
                current_user.launch_task(
                    "pipeline_pileup",
                    "run pileup pipeline",
                    dataset_id,
                    interval_id,
                    binsize
                )
    if Dataset.query.get(dataset_id).filetype == "bigwig":
        for binsize in binsizes:
            for interval_id in interval_ids:
                current_user.launch_task(
                    "pipeline_stackup",
                    "run stackup pipeline",
                    dataset_id,
                    interval_id,
                    binsize,
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
    if is_access_to_dataset_denied(Dataset.query.get(dataset_id), g):
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
        BedFileMetadata.query.get(metadata_id).associated_dataset, g
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


@api.route("/sessions/", methods=["POST"])
@auth.login_required
def create_session():
    """Creates a session with name."""

    def is_form_invalid():
        if not hasattr(request, "form"):
            return True
        if len(request.form) == 0:
            return True
        # check attributes
        if sorted(request.form.keys()) != ["name", "session_object", "session_type", "used_datasets"]:
            return True
        return False

    # check form
    if is_form_invalid():
        return invalid("Form is not valid!")
    # get data from form
    data = request.form
    name = data["name"]
    session_object = data["session_object"]
    session_type = data["session_type"]
    used_datasets = json.loads(data["used_datasets"])
    # check whether datasets exist
    datasets = [Dataset.query.get(dataset_id) for dataset_id in used_datasets]
    if any(dataset is None for dataset in datasets):
        return invalid(f"Some of the datasets in used_datasets do not exist!")
    # check whether dataset is owned
    if any(dataset.user_id != g.current_user.id for dataset in datasets):
        return forbidden(f"Some of the datasets associated with this session are not owned!")
    # create session
    session = Session(user_id=g.current_user.id,
                      name=name,
                      session_object=session_object,
                      session_type=session_type)
    # add datasets

    session.datasets.extend(datasets)
    db.session.add(session)
    db.session.commit()
    return jsonify({"session_id": f"{session.id}"})
