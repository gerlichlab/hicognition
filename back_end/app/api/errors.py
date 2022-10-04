""" Convenience functions for handling server errors."""
import logging
from flask.json import jsonify
from . import api

log = logging.getLogger()  # ASK What logger to use?


@api.app_errorhandler(404)
def page_not_found(_):
    """API error handler for 404"""
    response = jsonify({"error": "not found"})
    response.status_code = 404
    return response


@api.app_errorhandler(500)
def internal_server_error(e: Exception, msg: str = ""):
    """API error handler for 500"""
    log.exception(e)
    response = jsonify({"error": "Internal server error", "message": msg})
    response.status_code = 500
    return response


def forbidden(message):
    """API error handler for 403"""
    response = jsonify({"error": "forbidden", "message": message})
    response.status_code = 403
    return response


def not_found(message):
    """Convenience function that allows emission of 404 during request handling"""
    response = jsonify({"error": "not found", "message": message})
    response.status_code = 404
    return response


def invalid(message):
    """API error handler for 400"""
    response = jsonify({"error": "invalid request", "message": message})
    response.status_code = 400
    return response
