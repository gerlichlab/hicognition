from . import api
from .. import db
from ..models import User
from .authentication import auth
from flask.json import jsonify


@api.route('/test', methods=["GET"])
def test():
    """test api calls"""
    return jsonify({"test": "Hello, world!"})


@api.route('/testConf', methods=["GET"])
@auth.login_required
def test_conf():
    """test api calls"""
    return jsonify({"test": "Hello, world!"})