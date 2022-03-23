"""Init script for HiCognition API"""
from flask import Blueprint

api = Blueprint("api", __name__)

from . import (
    get_routes,
    post_routes,
    delete_routes,
    cross_origin,
    errors,
    authentication,
    initialization,
    put_routes,
)
