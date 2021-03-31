"""Config class for hicognition server."""
import os
import json

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Config class for hicognition server."""

    SECRET_KEY = os.environ.get("SECRET_KEY") or "eieieiei"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # TODO: check whether we still need this
    HIGLASS_URL = "http://localhost:8888"
    HIGLASS_API = "http://172.18.0.2:80/api/v1/tilesets/"  # this is the ipadress of the higlass container in the network
    UPLOAD_DIR = os.environ.get("UPLOAD_DIR") or os.path.join(basedir, "temp")
    CHROM_SIZES = os.environ.get("CHROM_SIZES") or os.path.join(
        basedir, "data/hg19.chrom.sizes"
    )
    CHROM_ARMS = os.environ.get("CHROM_ARMS") or os.path.join(basedir, "data/arms.hg19")
    HIGLASS_USER = os.environ.get("HIGLASS_USER") or "dummy"
    HIGLASS_PWD = os.environ.get("HIGLASS_PWD") or "xnVMhmKF7d^7"
    REDIS_URL = os.environ.get("REDIS_URL") or "redis://"
    WINDOW_SIZES = [200000, 300000, 400000]
    BIN_SIZES = [20000, 50000]  # In development mode, 10k hogs too much memory
    STACKUP_THRESHOLD = 100  # Threshold of when stackup is downsampled


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "app.db")


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL") or "sqlite://"
    UPLOAD_DIR = "./tmp_test"
    STACKUP_THRESHOLD = 10  # Threshold of when stackup is downsampled


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "data.sqlite")


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
