"""Init script for HiCognition"""
from flask import Flask
from .config import config
from flask_sqlalchemy import SQLAlchemy
from flask_sse import sse
from flask_login import LoginManager
from redis import Redis
import rq

db = SQLAlchemy()
login = LoginManager()

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
    db.init_app(app)
    # TODO: check if this is needed
    login.init_app(app)
    login.login_view = "login"
    # add redis queue
    app.redis = Redis.from_url(app.config["REDIS_URL"])
    app.queues = {
        "long": rq.Queue("hicognition-tasks-long", connection=app.redis),
        "medium": rq.Queue("hicognition-tasks-medium", connection=app.redis),
        "short": rq.Queue("hicognition-tasks-short", connection=app.redis),
    }
    # register api blueprint
    from .api import api as api_blueprint

    app.register_blueprint(api_blueprint, url_prefix="/api/")
    # register sse blueprint
    app.register_blueprint(sse, url_prefix="/stream")
    return app
