"""Config class for hicognition server."""
import os

# import json

basedir = os.path.abspath(os.path.dirname(__file__))

def _recursive_keys(metadata_dict: dict) -> set:
    keys = set()
    for key, value in metadata_dict.items():
        keys.add(key)
        if isinstance(value, dict):
            keys.update(_recursive_keys(value))
    return keys

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
    SHOWCASE = (
        bool(os.environ.get("SHOWCASE")) or False
    )  # if there is anything in showcase this is true

    # External repositories
    REPOSITORIES = [
        {
            "name": "4dn",
            "url": "https://data.4dnucleome.org/{href}",
            "file_url": "https://data.4dnucleome.org/files-processed/{id}",
            "auth_required": False,
        }
    ]

    # allowed binsizes for given windowsizes of regions
    PREPROCESSING_MAP = {
        50000: {
            "cooler": [5000],
            "bigwig": [1000, 2000],
            "collections": {
                "regions": [2000],
                "1d-features": [1000, 2000],
            },
        },
        100000: {
            "cooler": [5000],
            "bigwig": [2000, 5000, 10000],
            "collections": {
                "regions": [5000],
                "1d-features": [2000, 5000, 10000],
            },
        },
        400000: {
            "cooler": [10000],
            "bigwig": [5000, 10000, 20000],
            "collections": {
                "regions": [10000, 20000],
                "1d-features": [5000, 10000, 20000],
            },
        },
        1000000: {
            "cooler": [20000],
            "bigwig": [20000, 50000, 100000],
            "collections": {
                "regions": [20000, 50000],
                "1d-features": [20000, 50000, 100000],
            },
        },
        2000000: {
            "cooler": [50000],
            "bigwig": [50000, 100000, 200000],
            "collections": {
                "regions": [50000, 100000, 200000],
                "1d-features": [50000, 100000, 200000],
            },
        },
        "variable": {
            "cooler": [1, 2, 5],
            "bigwig": [1, 2, 5],
            "collections": {"regions": [1, 2, 5], "1d-features": [1, 2, 5]},
        },  # binsize for variable sizetype is in percent
    }
    # preprocessing maps for small genomic windowsizes
    PREPROCESSING_MAP_SMALL_WINDOWSIZES = {
        10000: {
            "cooler": [],
            "bigwig": [100, 500],
            "collections": {
                "regions": [1000],
                "1d-features": [100, 500],
            },
        },
        20000: {
            "cooler": [],
            "bigwig": [500, 1000],
            "collections": {
                "regions": [1000],
                "1d-features": [2000, 5000, 10000],
            },
        },
        50000: {
            "cooler": [2000],
            "bigwig": [1000, 2000],
            "collections": {
                "regions": [2000],
                "1d-features": [1000, 5000],
            },
        },
        "variable": {
            "cooler": [1, 2, 5],
            "bigwig": [1, 2, 5],
            "collections": {
                "regions": [1, 2, 5],
                "1d-features": [1, 2, 5],
            },
        },  # binsize for variable sizetype is in percent
    }
    VARIABLE_SIZE_EXPANSION_FACTOR = 0.2
    # mapping of pipeline names and queues to filetypes
    PIPELINE_NAMES = {
        "cooler": ("pipeline_pileup", "run pileup pipeline"),
        "bigwig": ("pipeline_stackup", "run stackup pipeline"),
        "collections": {
            "regions": ("pipeline_lola", "run lola pipeline"),
            "1d-features": ("pipeline_embedding_1d", "run 1d embedding pipeline"),
            "2d-features": ("pipeline_embedding_2d", "run 2d embedding pipeline"),
        },
    }
    # mapping of queue types to pipeline
    PIPELINE_QUEUES = {
        "cooler": "long",
        "bigwig": "medium",
        "collections": {
            "regions": "long",
            "1d-features": "medium",
            "2d-features": "long",
        },
    }
    CLUSTER_NUMBER_LARGE = 20
    CLUSTER_NUMBER_SMALL = 10
    
    FILETYPES = {
        "bedfile": {
            "dataset_type": ["region"],
            "file_ext": ["bed"],
            "metadata": [
                { # row 1
                    "Cell cycle Stage": "freetext",
                    "Perturbation": "freetext"
                },
                { # row 2
                    "ValueType":  {
                        "Peak": {
                            "Method": ["ChipSeq", "CutAndRun", "CutAndTag"],
                            # "Size Type": ["Point", "Interval"],
                            "Protein": "freetext",
                            "Directionality": ["+", "-", "No directionality"],
                        },
                        "Genome Annotation": {
                            # "Size Type": ["Point", "Interval"],
                            "Directionality": ["+", "-", "No directionality"],
                        },
                        "Derived": {
                            "Method": ["HiC", "Other Dataset"],
                            # "Size Type": ["Point", "Interval"],
                        }
                    }
                }
            ]
        },
        "bedpe_file": {
            "dataset_type": ["region"],
            "file_ext": ["bedpe"],
            "metadata": [
                { # row 1
                    "Cell cycle Stage": "freetext",
                    "Perturbation": "freetext"
                },
                { # row 2
                    "ValueType":  {
                        "Peak": {
                            "Method": ["ChipSeq", "CutAndRun", "CutAndTag"],
                            # "Size Type": ["Point", "Interval"],
                            "Protein": "freetext",
                            "Directionality": ["+", "-", "No directionality"],
                        },
                        "Genome Annotation": {
                            # "Size Type": ["Point", "Interval"],
                            "Directionality": ["+", "-", "No directionality"],
                        },
                        "Derived": {
                            "Method": ["HiC", "Other Dataset"],
                            # "Size Type": ["Point", "Interval"],
                        }
                    }
                }
            ]
        },
        "bigwig": {
            "dataset_type": "feature",
            "file_ext": ["bw", "bigwig"],
            "metadata": [
                {
                    "Cell cycle Stage": "freetext",
                    "Perturbation": "freetext",
                },
                {
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
                }
            ],
        },
        "cooler": {
            "dataset_type": "feature",
            "file_ext": ["mcool"],
            "metadata": [
                {
                    "Cell cycle Stage": "freetext",
                    "Perturbation": "freetext",
                },
                {
                    "ValueType": 
                    {
                        "Interaction": {
                            "Method": ["HiC"], 
                            "Normalization": ["ICCF"]
                        }
                    }
                }
            ]
        }
    }

    # Extract all metadata keys from config specification
    METADATA_KEYS = set()
    for file_type, file_type_config in FILETYPES.items():
        for row in file_type_config.get('metadata', []):
            METADATA_KEYS.update(_recursive_keys(row))

    # dataset-option mapping -> puts different optionvalues for dataset into relation
    DATASET_OPTION_MAPPING = {
        "supported_file_endings": {
            "bedfile": ["bed"],
            "cooler": ["mcool"],
            "bigwig": ["bw", "bigwig"],
        },
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
                    "Derived": {
                        "Method": ["HiC", "Other Dataset"],
                        "SizeType": ["Point", "Interval"],
                    },
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
        },
    }
    STACKUP_THRESHOLD = 500  # Threshold of when stackup is downsampled
    OBS_EXP_PROCESSES = (
        5  # Number of processes/worker to calculate obs/exp matrix of pileups
    )
    PILEUP_PROCESSES = 2  # Number of processes/worker to do pileups


class DevelopmentConfig(Config):
    """Config class for development server."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "app.db")


class TestingConfig(Config):
    """Config class for testing server."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    UPLOAD_DIR = "./tmp_test"
    STACKUP_THRESHOLD = 10  # Threshold of when stackup is downsampled


class End2EndConfig(DevelopmentConfig):
    """Extension of the development config class."""

    END2END = True


class ProductionConfig(Config):
    """Config class for production server."""

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "data.sqlite")


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
    "end2end": End2EndConfig,
}
