from . import api
from .. import db
from ..models import User
from flask.json import jsonify


@api.route('/test', methods=["GET"])
def test():
    """test api calls"""
    return jsonify({"test": "Hello, world!"})