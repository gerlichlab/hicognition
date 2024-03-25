# adds logging request handlers
from . import api
from flask import current_app, g, request


@api.after_app_request
def log_request(response):
    """Adds request logging"""
    if hasattr(g, "current_user") and g.current_user is not None:
        user_id = g.current_user.id
    else:
        user_id = None
    current_app.logger.info(f"ID {user_id} => {request.method} {request.url}")
    return response
