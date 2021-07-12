"""Config class for hicognition server."""
import os
import json

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Config class for hicognition server."""

    SECRET_KEY = os.environ.get("SECRET_KEY") or "eieieiei"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_DIR = os.environ.get("UPLOAD_DIR") or os.path.join(basedir, "temp")
    CHROM_SIZES = os.environ.get("CHROM_SIZES") or os.path.join(
        basedir, "data/hg19.chrom.sizes"
    )
    CHROM_ARMS = os.environ.get("CHROM_ARMS") or os.path.join(basedir, "data/arms.hg19")
    REDIS_URL = os.environ.get("REDIS_URL") or "redis://"
    # allowed binsizes for given windowsizes of regions -> pileups still fail for some combinations cannot be pickled -> FIXME: fix this
    PREPROCESSING_MAP = {
            50000: [1000, 2000, 5000],
            100000: [2000, 5000, 10000],
            400000: [5000, 10000, 20000],
            1000000: [20000, 50000, 100000],
            2000000: [50000, 100000, 200000],
    }
    # mapping of pipeline names to filetypes
    PIPELINE_NAMES = {
        "cooler": ("pipeline_pileup", "run pileup pipeline"),
        "bigwig": ("pipeline_stackup", "run stackup pipeline")
    }
    STACKUP_THRESHOLD = 500  # Threshold of when stackup is downsampled
    OBS_EXP_PROCESSES = 4 # Number of processes to use per worker to calcualte obs/exp matrix of pileups
    PILEUP_PROCESSES = 1 # Number of processes to use per worker to do pileups


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "app.db")


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
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
