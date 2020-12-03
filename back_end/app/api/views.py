"""API endpoints for hicognition"""
import os
import pandas as pd
import json
from flask.json import jsonify
from werkzeug.utils import secure_filename
from flask import g, request, current_app
from . import api
from .. import db
from ..models import Pileupregion, User, Dataset, Pileup
from .authentication import auth

# GET routes

@api.route('/test', methods=["GET"])
def test():
    """test api calls"""
    return jsonify({"test": "Hello, world!"})


@api.route('/testProtected', methods=["GET"])
@auth.login_required
def test_protected():
    """test api calls"""
    return jsonify({"test": "Hello, world!"})


@api.route('/datasets/', methods=["GET"])
@auth.login_required
def get_all_datasets():
    """Gets all available datasets for a given user."""
    all_files = Dataset.query.filter(Dataset.user_id == g.current_user.id).all()
    update_processing_state(all_files, db)
    return jsonify([dfile.to_json() for dfile in all_files])


@api.route('/datasets/<dtype>', methods=["GET"])
@auth.login_required
def get_datasets(dtype):
    """Gets all available datasets for a given user."""
    if dtype == "cooler":
        cooler_files = Dataset.query.filter((Dataset.filetype == "cooler") & (g.current_user.id == Dataset.user_id)).all()
        update_processing_state(cooler_files, db)
        return jsonify([cfile.to_json() for cfile in cooler_files])
    elif dtype == "bed":
        bed_files = Dataset.query.filter((Dataset.filetype == "bedfile") & (g.current_user.id == Dataset.user_id)).all()
        update_processing_state(bed_files, db)
        return jsonify([bfile.to_json() for bfile in bed_files])
    else:
        response = jsonify({"error": f"option: '{dtype}' not understood"})
        response.status_code = 404
        return response


@api.route('/datasets/<dataset_id>/pileupregions/', methods=["GET"])
@auth.login_required
def get_pileupregiones_of_dataset(dataset_id):
    """Gets all available pileupregions for a given dataset, if the user owns the requested dataset."""
    dataset = Dataset.query.get(dataset_id)
    # check whether dataset exists
    if dataset is None:
        response = jsonify({"error": f"Dataset with id '{dataset_id}' does not exist!"})
        response.status_code = 404
        return response
    # check whether user owns the dataset
    if is_access_to_dataset_denied(dataset, g.current_user):
        response = jsonify({"error": f"Dataset with id '{dataset_id}' is not owned by logged in user!"})
        response.status_code = 403
        return response
    # SQL join to get all pileupregions that come from the specified dataset
    all_files = Pileupregion.query.join(Dataset).filter((Dataset.user_id == g.current_user.id) & (Dataset.id == dataset_id)).all()
    return jsonify([dfile.to_json() for dfile in all_files])


@api.route('/pileupregions/', methods=["GET"])
@auth.login_required
def get_pileupregions():
    """Gets all available pileupregions for a given user."""
    # SQL join to get all pileupregions that come from a dataset owned by the respective user
    all_files = Pileupregion.query.join(Dataset).filter(Dataset.user_id == g.current_user.id).all()
    return jsonify([dfile.to_json() for dfile in all_files])


@api.route('/pileups/<cooler_id>/<pileupregion_id>/', methods=["GET"])
@auth.login_required
def get_pileups(cooler_id, pileupregion_id):
    """Gets all available pileups from a given cooler file
    for the specified pileupregion_id. Only returns pileup object if
    user owns the cooler dataset and pileupregion_id"""
    # Check whether datasets exist
    cooler_ds = Dataset.query.get(cooler_id)
    pileupregion_ds = Pileupregion.query.get(pileupregion_id)
    if (cooler_ds is None) or (pileupregion_ds is None):
        response = jsonify({"error": f"Cooler dataset or pileupregion dataset do not exist!"})
        response.status_code = 404
        return response
    # Check whether datasets are owned
    if is_access_to_dataset_denied(cooler_ds, g.current_user) or is_access_to_dataset_denied(pileupregion_ds.source_dataset, g.current_user):
        response = jsonify({"error": f"Cooler dataset or pileupregion dataset is not owned by logged in user!"})
        response.status_code = 403
        return response
    # return all pileupregions the are derived from the specified selection of cooler and pileupregion
    all_files = Pileup.query.filter(Pileup.pileupregion_id == pileupregion_id).join(Dataset).filter(Dataset.id == cooler_id).all()
    return jsonify([dfile.to_json() for dfile in all_files])


#TODO: /pileups/<pileup_id>/data 
@api.route('/pileups/data/<pileup_id>/', methods=["GET"])
@auth.login_required
def get_pileup_data(pileup_id):
    """returns pileup data for the specified pileup id if it exists and
    the user is owner."""
    # Check for existence
    if (Pileup.query.get(pileup_id) is None):
        response = jsonify({"error": f"Pileup does not exist!"})
        response.status_code = 404
        return response
    # Check whether datasets are owned
    pileup = Pileup.query.get(pileup_id)
    cooler_ds = pileup.source_cooler
    bed_ds = pileup.source_pileupregion.source_dataset
    if is_access_to_dataset_denied(cooler_ds, g.current_user) or is_access_to_dataset_denied(bed_ds, g.current_user):
        response = jsonify({"error": f"Cooler dataset or bed dataset is not owned by logged in user!"})
        response.status_code = 403
        return response
    # dataset is owned, return the data
    csv_data = pd.read_csv(pileup.file_path)
    json_data = csv_data.to_json()
    return jsonify(json_data)


# POST routes

@api.route('/datasets/', methods=["POST"])
@auth.login_required
def add_dataset():
    """endpoint to add a new dataset"""
    current_user = g.current_user
    # get data from form
    data = request.form
    fileObject = request.files["file"]
    # add data to Database -> in order to show uploading
    new_entry = Dataset(
        dataset_name = data["datasetName"],
        processing_state = "uploading",
        filetype=data["filetype"],
        user_id=current_user.id
    )
    db.session.add(new_entry)
    db.session.commit()
    # save file in upload directory
    filename = secure_filename(fileObject.filename)
    file_path = os.path.join(current_app.config["UPLOAD_DIR"], filename)
    fileObject.save(file_path)
    if data["filetype"] not in ["cooler", "bedfile"]:
        response = jsonify({"error": "datatype not understood"})
        response.status_code = 403
        return response
    # add file_path to database entr
    new_entry.file_path = file_path
    new_entry.processing_state = "uploaded"
    db.session.add(new_entry)
    db.session.commit()
    # start preprocessing
    if data["filetype"] == "bedfile":
        current_user.launch_task("pipeline_bed", "run bed preprocessing", new_entry.id)
        db.session.commit()
    else:
        current_user.launch_task("pipeline_cooler", "run cooler preprocessing", new_entry.id)
        db.session.commit()
    return jsonify({"message": "success! Preprocessing triggered."})


@api.route('/preprocess/', methods=["POST"])
@auth.login_required
def preprocess_dataset():
    """Starts preprocessing pipeline
    for datasets specified in the request body"""
    def is_form_invalid():
        if not hasattr(request, "form"):
            return True
        if sorted(list(request.form.keys())) != sorted(["dataset_id", "binsizes", "pileup_region_ids"]):
            return True
        return False
    current_user = g.current_user
    # check form
    if is_form_invalid():
        response = jsonify({"error": f"Form is not valid!"})
        response.status_code = 400
        return response
    # get data from form
    data = request.form
    dataset_id = json.loads(data["dataset_id"])
    binsizes = json.loads(data["binsizes"])
    pileup_region_ids = json.loads(data["pileup_region_ids"])
    # check whether dataset exists
    if Dataset.query.get(dataset_id) is None:
        response = jsonify({"error": f"Dataset does not exist!"})
        response.status_code = 404
        return response
    if is_access_to_dataset_denied(Dataset.query.get(dataset_id), g.current_user):
        response = jsonify({"error": f"Cooler dataset is not owned by logged in user!"})
        response.status_code = 403
        return response
    current_user.launch_task("pipeline_pileup", "run pileup pipeline", dataset_id, binsizes, pileup_region_ids)
    db.session.commit()
    return jsonify({"message": "success! Preprocessing triggered."})

# fix cross-origin problems. From https://gist.github.com/davidadamojr/465de1f5f66334c91a4c
@api.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

# helpers


def is_access_to_dataset_denied(dataset_id, current_user):
    """Checks whether access to a certian dataset is denied
    for a given user."""
    return dataset_id.user_id != current_user.id


def update_processing_state(datasets, db):
    """updates processing state of all datasets in the supplied iterabel"""
    for dataset in datasets:
        dataset.set_processing_state(db)