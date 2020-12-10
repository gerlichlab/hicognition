from . import api
from flask.json import jsonify


@api.app_errorhandler(404)
def page_not_found(e):
    """API error handler for 404"""
    response = jsonify({"error": "not found"})
    response.status_code = 404
    return response


@api.app_errorhandler(500)
def internal_server_error(e):
    """API error handler for 500"""
    response = jsonify({"error": "Internal server error."})
    response.status_code = 500
    return response


def forbidden(message):
    response = jsonify({"error": "forbidden", "message": message})
    response.status_code = 403
    return response


def not_found(message):
    """Convenience function that allows emission of 404 during request handling"""
    response = jsonify({"error": "not found", "message": message})
    response.status_code = 404
    return response


def invalid(message):
    response = jsonify({"error": "invalid request", "message": message})
    response.status_code = 400
    return response
