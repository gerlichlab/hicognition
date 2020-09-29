from . import api
from flask.json import jsonify


@api.app_errorhandler(404)
def page_not_found(e):
    """test api calls"""
    response = jsonify({"error": "not found"})
    response.status_code = 404
    return response


def forbidden(message):
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response