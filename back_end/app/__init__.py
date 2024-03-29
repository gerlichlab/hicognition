"""Init script for HiCognition"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_sse import sse
from flask_mail import Mail
import rq
from redis import Redis
from .logging_utils import create_logging_config
from .config.app_config import config
from .confirmation import ConfirmationHandler

db = SQLAlchemy()
mail = Mail()
confirmation_handler = ConfirmationHandler(mail_client=mail)

# create sse request handler


@sse.after_request
def add_sse_headers(response):
    """Adds sse specific headers"""
    response.headers["X-Accel-Buffering"] = "no"
    response.headers["Cache-Control"] = "no-cache"
    return response


def create_app(config_name):
    """factory to create app."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    create_logging_config(config[config_name])
    # init db
    db.init_app(app)
    # add redis queue
    app.redis = Redis.from_url(app.config["REDIS_URL"])
    app.queues = {
        "long": rq.Queue("hicognition-tasks-long", connection=app.redis),
        "medium": rq.Queue("hicognition-tasks-medium", connection=app.redis),
        "short": rq.Queue("hicognition-tasks-short", connection=app.redis),
    }
    # register api blueprint
    with app.app_context():
        from .api import api as api_blueprint

    app.register_blueprint(api_blueprint, url_prefix="/api/")
    # register sse blueprint
    if not app.config["SHOWCASE"]:
        app.register_blueprint(sse, url_prefix="/stream")
    # add mail handler
    mail.init_app(app)
    # add token handler
    confirmation_handler.init_app(app)
    return app
