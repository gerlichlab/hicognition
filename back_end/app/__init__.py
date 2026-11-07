"""Init script for HiCognition"""

import rq
from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_sse import sse
from redis import Redis

from .config.app_config import config
from .confirmation import ConfirmationHandler
from .logging_utils import create_logging_config

# the values of the example .env in the repository, which anyone can read
PUBLISHED_SECRETS = {"eieieiei", "blblblbl"}

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


def check_secrets(app_config, production):
    """Raises unless the secrets that sign tokens and links are set, and in production, unless
    they differ from the example .env's."""
    if app_config["TESTING"]:
        return
    for name in ("SECRET_KEY", "SECRET_SALT"):
        value = app_config.get(name)
        if not value:
            raise RuntimeError(
                f"{name} is not set. Set it in .env, for example to the output of "
                "`openssl rand -hex 32`."
            )
        if production and value in PUBLISHED_SECRETS:
            raise RuntimeError(
                f"{name} has the value of the example .env, which anyone can read. Set it in "
                ".env to a value of your own, for example the output of `openssl rand -hex 32`."
            )


def create_app(config_name):
    """factory to create app."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    check_secrets(app.config, production=config_name == "production")
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
