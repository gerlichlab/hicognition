"""GET API endpoints for hicognition"""
from flask.globals import current_app
import pandas as pd
from flask.json import jsonify
from flask import g, request
from .helpers import update_processing_state, is_access_to_dataset_denied
from . import api
from .. import db
from ..models import Intervals, Dataset, AverageIntervalData
from .authentication import auth
from .errors import forbidden, not_found, invalid


@api.route("/test", methods=["GET"])
def test():
    """test api calls"""
    return jsonify({"test": "Hello, world!"})


@api.route("/testProtected", methods=["GET"])
@auth.login_required
def test_protected():
    """test api calls"""
    return jsonify({"test": "Hello, world!"})


@api.route("/datasets/", methods=["GET"])
@auth.login_required
def get_all_datasets():
    """Gets all available datasets for a given user."""
    current_app.logger.warn("Get datasets called!")
    all_files = Dataset.query.filter(Dataset.user_id == g.current_user.id).all()
    update_processing_state(all_files, db)
    return jsonify([dfile.to_json() for dfile in all_files])


@api.route("/datasets/<dtype>", methods=["GET"])
@auth.login_required
def get_datasets(dtype):
    """Gets all available datasets for a given user."""
    if dtype == "cooler":
        cooler_files = Dataset.query.filter(
            (Dataset.filetype == "cooler") & (g.current_user.id == Dataset.user_id)
        ).all()
        update_processing_state(cooler_files, db)
        return jsonify([cfile.to_json() for cfile in cooler_files])
    elif dtype == "bed":
        bed_files = Dataset.query.filter(
            (Dataset.filetype == "bedfile") & (g.current_user.id == Dataset.user_id)
        ).all()
        update_processing_state(bed_files, db)
        return jsonify([bfile.to_json() for bfile in bed_files])
    else:
        return not_found(f"option: '{dtype}' not understood")


@api.route("/datasets/<dataset_id>/intervals/", methods=["GET"])
@auth.login_required
def get_intervals_of_dataset(dataset_id):
    """Gets all available intervals for a given dataset, if the user owns the requested dataset."""
    dataset = Dataset.query.get(dataset_id)
    # check whether dataset exists
    if dataset is None:
        return not_found(f"Dataset with id '{dataset_id}' does not exist!")
    # check whether user owns the dataset
    if is_access_to_dataset_denied(dataset, g.current_user):
        return forbidden(f"Dataset with id '{dataset_id}' is not owned by logged in user!")
    # SQL join to get all intervals that come from the specified dataset
    all_files = (
        Intervals.query.join(Dataset)
        .filter((Dataset.user_id == g.current_user.id) & (Dataset.id == dataset_id))
        .all()
    )
    return jsonify([dfile.to_json() for dfile in all_files])


@api.route("/intervals/", methods=["GET"])
@auth.login_required
def get_intervals():
    """Gets all available intervals for a given user."""
    # SQL join to get all intervals that come from a dataset owned by the respective user
    all_files = (
        Intervals.query.join(Dataset)
        .filter(Dataset.user_id == g.current_user.id)
        .all()
    )
    return jsonify([dfile.to_json() for dfile in all_files])


@api.route("/averageIntervalData/", methods=["GET"])
@auth.login_required
def get_averageIntervalData():
    """Gets all available averageIntervalData from a given cooler file
    for the specified intervals_id. Only returns pileup object if
    user owns the cooler dataset and intervals_id"""
    # unpack query string
    cooler_id = request.args.get("cooler_id")
    intervals_id = request.args.get("intervals_id")
    if cooler_id is None or intervals_id is None:
        return invalid("Cooler dataset or intervals were not specified!")
    # Check whether datasets exist
    cooler_ds = Dataset.query.get(cooler_id)
    intervals_ds = Intervals.query.get(intervals_id)
    if (cooler_ds is None) or (intervals_ds is None):
        return not_found("Cooler dataset or intervals dataset do not exist!")
    # Check whether datasets are owned
    if is_access_to_dataset_denied(
        cooler_ds, g.current_user
    ) or is_access_to_dataset_denied(intervals_ds.source_dataset, g.current_user):
        return forbidden("Cooler dataset or intervals dataset is not owned by logged in user!")
    # return all intervals the are derived from the specified selection of cooler and intervals
    all_files = (
        AverageIntervalData.query.filter(AverageIntervalData.intervals_id == intervals_id)
        .join(Dataset)
        .filter(Dataset.id == cooler_id)
        .all()
    )
    return jsonify([dfile.to_json() for dfile in all_files])


@api.route("/averageIntervalData/<pileup_id>/", methods=["GET"])
@auth.login_required
def get_pileup_data(pileup_id):
    """returns pileup data for the specified pileup id if it exists and
    the user is owner."""
    # Check for existence
    if AverageIntervalData.query.get(pileup_id) is None:
        return not_found("Pileup does not exist!")
    # Check whether datasets are owned
    pileup = AverageIntervalData.query.get(pileup_id)
    cooler_ds = pileup.source_cooler
    bed_ds = pileup.source_intervals.source_dataset
    if is_access_to_dataset_denied(
        cooler_ds, g.current_user
    ) or is_access_to_dataset_denied(bed_ds, g.current_user):
        return forbidden("Cooler dataset or bed dataset is not owned by logged in user!")
    # dataset is owned, return the data
    csv_data = pd.read_csv(pileup.file_path)
    json_data = csv_data.to_json()
    return jsonify(json_data)
