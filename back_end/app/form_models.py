"""Pydantic models to validate integrity of Forms for the HiCognition API."""
from pydantic import BaseModel, Field, validator, constr
from flask import current_app


# pylint: disable=no-self-argument,no-self-use
class DatasetPostModel(BaseModel):
    """Is a model of the dataset upload form."""

    dataset_name: constr(min_length=3, max_length=81) = Field(..., alias="datasetName")
    public: bool
    assembly: int
    description: constr(max_length=81) = Field("No description provided")
    normalization: constr(max_length=64) = Field("undefined", alias="Normalization")
    method: constr(max_length=64) = Field("undefined", alias="Method")
    size_type: constr(max_length=64) = Field("undefined", alias="SizeType")
    directionality: constr(max_length=64) = Field("undefined", alias="Directionality")
    derivation_type: constr(max_length=64) = Field("undefined", alias="DerivationType")
    protein: constr(max_length=64) = Field("undefined", alias="Protein")
    cell_cycle_stage: constr(max_length=64) = Field(..., alias="cellCycleStage")
    perturbation: constr(max_length=64)
    user_id: int = None
    processing_state: constr(max_length=64) = None
    filetype: constr(max_length=64)
    filename: constr(max_length=200)
    value_type: constr(max_length=64) = Field(..., alias="ValueType")
    source_url: constr(max_length=512) = Field(alias="SourceURL")
    sample_id: constr(max_length=128) = Field(alias="sampleID")
    repository_name: constr(max_length=64) = Field(alias="RepositoryName")
    file_type: str # TODO

    @classmethod
    def get_reverse_alias(cls, key):
        """Returns the reverse alias i.e. the pydantic field name if provided the front-end alias."""
        alias_table = {
            "datasetName": "dataset_name",
            "Normalization": "normalization",
            "Method": "method",
            "SizeType": "size_type",
            "Directionality": "directionality",
            "DerivationType": "derivation_type",
            "Protein": "protein",
            "cellCycleStage": "cell_cycle_stage",
            "ValueType": "value_type",
            "SampleID": "sample_id",
            "RepositoryName": "repository_name",
            "SourceURL": "source_url"
        }
        return alias_table[key]

    class Config:
        """Sets up the alias generator"""

        allow_population_by_field_name = True
        extra = "forbid"

    @validator("value_type")
    def value_type_supported_in_dataset_attribute_mapping(
        cls, value_type, values, **kwargs
    ):
        """Checks whether value_type passed dataset_attribute_mapping."""
        dataset_type_mapping = current_app.config["DATASET_OPTION_MAPPING"][
            "DatasetType"
        ]
        if values["filetype"] not in dataset_type_mapping.keys():
            raise ValueError(
                f'Unsupported filetype! We do not support following filetype: {values["filetype"]}. Supported filestypes are: {dataset_type_mapping.keys()}.'
            )
        value_types = dataset_type_mapping[values["filetype"]]["ValueType"]
        # checks if the particular value_type is defined in the app config
        if value_type not in value_types.keys():
            raise ValueError(
                f'Unsupported value_type! We do not support value_type: {value_type} for the filetype {values["filetype"]}. We support {value_types.keys()}.'
            )
        # check value type members
        for key, possible_values in value_types[value_type].items():
            # check whether field is freetext
            if possible_values == "freetext":
                continue
            # check that value in form corresponds to possible values
            # this will also check if all mandatory keys are provided since "undefined" is not in possible_values
            if values[cls.get_reverse_alias(key)] not in possible_values:
                raise ValueError(
                    f"Unsupported possible value '{values[cls.get_reverse_alias(key)]}' for value_type: {value_type}. Supported values {possible_values}."
                )
        return value_type


    @validator("description")
    def parse_description(cls, description):
        """Checks if description was provided provided in frontend, if not rewrites it."""
        if description == "null":
            description = "No description provided"
        return description

    def __getitem__(self, item):
        if hasattr(self, item):
            return getattr(self, item)
        return getattr(self, self.get_reverse_alias(item))

    def __contains__(self, item):
        return hasattr(self, item)

class FileDatasetPostModel(DatasetPostModel):
    """model of dataset with file"""
    
    @validator("filename")
    def file_has_correct_ending_and_supported_filetype(cls, filename, values, **kwargs):
        """Checks is the file has the appropriate file ending."""
        supported_file_endings = current_app.config["DATASET_OPTION_MAPPING"][
            "supported_file_endings"
        ]
        file_ending = filename.split(".")[-1]
        if values["filetype"] not in supported_file_endings:
            raise ValueError(
                f'Unsupported filetype! We do not support following filetype: {values["filetype"]}. Supported filestypes and endings are: {supported_file_endings}.'
            )
        if file_ending.lower() not in supported_file_endings[values["filetype"]]:
            raise ValueError(
                f'Invalid filename! For the filetype: {values["filetype"]} we found the file ending: {file_ending}. Supported for this filetype are: {supported_file_endings[values["filetype"]]}.'
            )
        return filename