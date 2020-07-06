"""Config class for hicognition server."""
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config():
    """Config class for hicognition server."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'eieieiei'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    HIGLASS_URL = "http://localhost:8888"
    DEFAULT_CONFIG = "default_config.json"
