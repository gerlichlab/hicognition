"""Init script for HiCognition"""
import os
import logging
from flask import Flask
from flask_restx import Api
from flask_marshmallow import Marshmallow
import app.database as db

api = Api()
ma = Marshmallow()

def create_app(config):
    """factory to create app."""
    app = Flask(__name__)
    app.config.from_object(config)
    app.config['SECRET_KEY'] = 'secret key here'
    api.init_app(app)
    ma.init_app(app)
    logging.basicConfig(level=app.config['LOGGING'])
    db.initialize(app.config['SQL_CONNECTOR'])
    
    app.session = db.session
    
    if not os.path.exists(app.config['FILEUPLOAD_DIR']):
        os.mkdir(app.config['FILEUPLOAD_DIR'])


    @app.teardown_appcontext
    def _teardown(exception = ""):
        logging.exception(f"Tearing down instance. {exception}")
        db.shutdown()
    
    from app.services.file import file_service
    file_service.init_app(app)
    
    from app.routes import user, file, featuresets, calculations
    
    # from app.daos.daos import user_dao
    # from app.models import User
    # user_dao.add(User(username='dev', password_hash='asdf', email='dev@devteam.at'))
    # db.session.commit()
    
    return app
    # app.config.from_object(config[config_name])
    # db.init_app(app)
    # # add redis queue
    # app.redis = Redis.from_url(app.config["REDIS_URL"])
    # app.queues = {
    #     "long": rq.Queue("hicognition-tasks-long", connection=app.redis),
    #     "medium": rq.Queue("hicognition-tasks-medium", connection=app.redis),
    #     "short": rq.Queue("hicognition-tasks-short", connection=app.redis),
    # }
    # # register api blueprint
    # with app.app_context():
    #     from .api import api as api_blueprint

    # app.register_blueprint(api_blueprint, url_prefix="/api/")
    # # register sse blueprint
    # if not app.config["SHOWCASE"]:
    #     app.register_blueprint(sse, url_prefix="/stream")
    # return app