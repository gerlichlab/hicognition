"""API endpoints for hicognition"""
from . import api
from .. import db
from ..models import User, Dataset
from .authentication import auth
from flask.json import jsonify
from flask import g, request


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

@api.route('/testQ/',methods=["GET"])
def test_queue():
    """endpoint to test queue"""
    dummy = User.query.get(1)
    dummy.launch_task('example', "TEST", 20)
    db.session.commit()
    return jsonify({"result": "dispatched"})


# fix cross-origin problems. From https://gist.github.com/davidadamojr/465de1f5f66334c91a4c
@api.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response