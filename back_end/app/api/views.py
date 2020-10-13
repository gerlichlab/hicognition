"""API endpoints for hicognition"""
import os
import pdb
from flask.json import jsonify
from werkzeug.utils import secure_filename
from flask import g, request, current_app
from . import api
from .. import db
from ..models import Pileupregion, User, Dataset
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
    return jsonify([dfile.to_json() for dfile in all_files])


@api.route('/datasets/<dtype>', methods=["GET"])
@auth.login_required
def get_datasets(dtype):
    """Gets all available datasets for a given user."""
    if dtype == "cooler":
        cooler_files = Dataset.query.filter((Dataset.filetype == "cooler") & (g.current_user.id == Dataset.user_id)).all()
        return jsonify([cfile.to_json() for cfile in cooler_files])
    elif dtype == "bed":
        bed_files = Dataset.query.filter((Dataset.filetype == "bedfile") & (g.current_user.id == Dataset.user_id)).all()
        return jsonify([bfile.to_json() for bfile in bed_files])
    else:
        response = jsonify({"error": f"option: '{dtype}' not understood"})
        response.status_code = 404
        return response


@api.route('/datasets/<dataset_id>/pileupregions/', methods=["GET"])
@auth.login_required
def get_pileupregiones_of_dataset(dataset_id):
    """Gets all available pileupregions for a given dataset, if the user owns the requested dataset."""
    # check whether dataset exists
    if Dataset.query.get(dataset_id) is None:
        response = jsonify({"error": f"Dataset with id '{dataset_id}' does not exist!"})
        response.status_code = 404
        return response
    # check whether user owns the dataset
    if Dataset.query.get(dataset_id).user_id != g.current_user.id:
        response = jsonify({"error": f"Dataset with id '{dataset_id}' is not owend by logged in uwer!"})
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


# POST routes

@api.route('/datasets/', methods=["POST"])
@auth.login_required
def add_dataset():
    """endpoint to add a new dataset"""
    current_user = g.current_user
    # get data from form
    data = request.form
    fileObject = request.files["file"]
    # save file in upload directory
    filename = secure_filename(fileObject.filename)
    file_path = os.path.join(current_app.config["UPLOAD_DIR"], filename)
    fileObject.save(file_path)
    if data["filetype"] not in ["cooler", "bedfile"]:
        response = jsonify({"error": "datatype not understood"})
        response.status_code = 403
        return response
    # add data to Database
    new_entry = Dataset(
        dataset_name = data["datasetName"],
        file_path=file_path,
        filetype=data["filetype"],
        user_id=current_user.id
    )
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


# fix cross-origin problems. From https://gist.github.com/davidadamojr/465de1f5f66334c91a4c
@api.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response