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
    TESTING = False
    END2END = False
    # allowed binsizes for given windowsizes of regions
    PREPROCESSING_MAP = {
        50000: [1000, 2000, 5000],
        100000: [2000, 5000, 10000],
        400000: [5000, 10000, 20000],
        1000000: [20000, 50000, 100000],
        2000000: [50000, 100000, 200000],
        "variable": [1, 2, 5],  # binsize for variable sizetype is in percent
    }
    VARIABLE_SIZE_EXPANSION_FACTOR = 0.2
    # mapping of pipeline names to filetypes
    PIPELINE_NAMES = {
        "cooler": ("pipeline_pileup", "run pileup pipeline"),
        "bigwig": ("pipeline_stackup", "run stackup pipeline"),
        "collections": {
            "regions": ("pipeline_lola", "run lola pipeline"),
            "1d-features": ("pipeline_embedding_1d", "run 1d embedding pipeline"),
        },
    }
    # dataset-option mapping -> puts different optionvalues for dataset into relation
    DATASET_OPTION_MAPPING = {
        "DatasetType": {
            "bedfile": {
                "ValueType": {
                    "Peak": {
                        "Method": ["ChipSeq", "CutAndRun", "CutAndTag"],
                        "SizeType": ["Point", "Interval"],
                        "Protein": "freetext",
                        "Directionality": ["+", "-", "No directionality"],
                    },
                    "GenomeAnnotation": {
                        "SizeType": ["Point", "Interval"],
                        "Directionality": ["+", "-", "No directionality"],
                    },
                    "Derived": {"Method": ["HiC"], "SizeType": ["Point", "Interval"]},
                }
            },
            "bigwig": {
                "ValueType": {
                    "Derived": {
                        "Normalization": ["Base-line-correct", "No Normalization"],
                        "DerivationType": ["InsulationScore", "PairingScore"],
                        "Method": ["HiC"],
                    },
                    "ChromatinAssociation": {
                        "Protein": "freetext",
                        "Method": ["ChipSeq", "CutAndRun", "CutAndTag"],
                        "Normalization": ["NormToControl", "RPM", "No Normalization"],
                    },
                    "GeneExpression": {
                        "Normalization": [
                            "NormToControl",
                            "RPM",
                            "RPKM",
                            "No Normalization",
                        ],
                        "Method": ["RNAseq", "GroSeq", "SLAMseq", "NETseq"],
                    },
                }
            },
            "cooler": {
                "ValueType": {
                    "Interaction": {"Method": ["HiC"], "Normalization": ["ICCF"]}
                }
            },
        }
    }
    STACKUP_THRESHOLD = 500  # Threshold of when stackup is downsampled
    OBS_EXP_PROCESSES = (
        4
    )  # Number of processes to use per worker to calcualte obs/exp matrix of pileups
    PILEUP_PROCESSES = 1  # Number of processes to use per worker to do pileups


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

class End2EndConfig(DevelopmentConfig):
    END2END = True
    pass


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "data.sqlite")


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
    "end2end": End2EndConfig
}
