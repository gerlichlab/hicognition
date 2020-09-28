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
    HIGLASS_API = "http://172.18.0.2:80/api/v1/tilesets/"  # this is the ipadress of the higlass container in the network
    DEFAULT_CONFIG = "default_config.json"
    UPLOAD_DIR = os.environ.get('UPLOAD_DIR') or os.path.join(basedir, "temp")
    CHROM_SIZES = os.environ.get("CHROM_SIZES") or os.path.join(basedir, "data/hg19.chrom.sizes")
    HIGLASS_USER = os.environ.get("HIGLASS_USER") or "dummy"
    HIGLASS_PWD = os.environ.get("HIGLASS_PWD") or 'xnVMhmKF7d^7'
