"""Init script for HiCognition API"""
from flask import Blueprint, current_app

api = Blueprint("api", __name__, template_folder="../templates")

if current_app.config["SHOWCASE"]:
    from . import (
        get_routes,
        cross_origin,
        errors,
        authentication,
        initialization,
    )
else:
    from . import (
        get_routes,
        post_routes,
        delete_routes,
        cross_origin,
        errors,
        authentication,
        initialization,
        put_routes,
        request_logger,
    )
