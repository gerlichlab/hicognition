"""Init script for HiCognition API"""

# The imports register each module's routes, error handlers and request hooks on the
# blueprint.
# ruff: noqa: F401

from flask import Blueprint, current_app

api = Blueprint("api", __name__, template_folder="../templates")

if current_app.config["SHOWCASE"]:
    from . import (
        authentication,
        cross_origin,
        errors,
        get_routes,
        initialization,
    )
else:
    from . import (
        authentication,
        cross_origin,
        delete_routes,
        errors,
        get_routes,
        initialization,
        post_routes,
        put_routes,
        request_logger,
    )
