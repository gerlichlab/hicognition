"""Pydantic models to validate integrity of Forms for the HiCognition API."""
import re
from pydantic import BaseModel, Field, validator, constr, AnyUrl

from flask import current_app


class UserRegistrationModel(BaseModel):
    user_name: constr(min_length=3, max_length=81) = Field(..., alias="userName")
    email_address: str = Field(..., alias='emailAddress') # TODO: validate email
    password: constr(min_length=5) = Field(..., alias="password1")


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
    processing_state: constr(max_length=64) = None
    filetype: constr(max_length=64) = Field("undefined", alias="filetype")
    value_type: constr(max_length=64) = Field("undefined", alias="ValueType")

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
            "sampleID": "sample_id",
            "repositoryName": "repository_name",
            "sourceURL": "source_url",
            "filetype": "filetype",
        }
        return alias_table.get(key)

    class Config:
        """Sets up the alias generator"""

        allow_population_by_field_name = True
        extra = "forbid"

    @validator("filetype")
    def check_filetype(cls, filetype, values, **kwargs):
        supported_file_endings = current_app.config["DATASET_OPTION_MAPPING"][
            "supported_file_endings"
        ]
        if not filetype:
            raise ValueError(
                f"Filetype is required! Supported filestypes and endings are: {supported_file_endings}."
            )
        if filetype not in supported_file_endings:
            raise ValueError(
                f"Unsupported filetype! We do not support following filetype: {filetype}. Supported filestypes and endings are: {supported_file_endings}."
            )
        return filetype

    @validator("value_type")
    def value_type_supported_in_dataset_attribute_mapping(
        cls, value_type, values, **kwargs
    ):
        """Checks whether value_type passed dataset_attribute_mapping."""
        dataset_type_mapping = current_app.config["DATASET_OPTION_MAPPING"][
            "DatasetType"
        ]
        if not values.get("filetype"):
            raise ValueError("No valid file type has been provided.")

        value_types = dataset_type_mapping.get(values.get("filetype"), dict()).get(
            "ValueType", dict()
        )
        # checks if the particular value_type is defined in the app config
        if value_type not in value_types.keys():
            raise ValueError(
                f'Unsupported value_type! We do not support value_type: {value_type} for the filetype \'{values.get("filetype")}\'. We support {value_types.keys()}.'
            )
        # check value type members
        for key, possible_values in value_types[value_type].items():
            if cls.get_reverse_alias(key) not in values:
                import pdb

                pdb.set_trace()
            # check whether field is freetext
            if possible_values == "freetext":
                continue
            # check that all needed values are found
            if cls.get_reverse_alias(key) not in values:
                raise ValueError(
                    f"Required argument '{cls.get_reverse_alias(key)}' for '{value_type}' not found. Supported arguments {value_types[value_type].keys()}."
                )
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

    filename: constr(max_length=200)

    @validator("filename")
    def file_has_correct_ending_and_supported_filetype(cls, filename, values, **kwargs):
        """Checks is the file has the appropriate file ending."""
        supported_file_endings = current_app.config["DATASET_OPTION_MAPPING"][
            "supported_file_endings"
        ]
        file_ending = filename.split(".")[-1]
        if file_ending.lower() not in supported_file_endings.get(
            values.get("filetype")
        ):
            raise ValueError(
                f'Invalid filename! For the filetype: {values.get("filetype")} we found the file ending: {file_ending}. Supported for this filetype are: {supported_file_endings.get(values.get("filetype"))}.'
            )
        return filename


class URLDatasetPostModel(DatasetPostModel):
    """model of dataset with an URL"""

    source_url: AnyUrl = Field(alias="sourceURL")


class ENCODEDatasetPostModel(DatasetPostModel):
    """model of dataset with an URL"""

    sample_id: constr(max_length=128) = Field(alias="sampleID")
    repository_name: constr(max_length=64) = Field(alias="repositoryName")

    # @validator("sample_id")
    # def sample_id_exists(cls, sample_id):
    #     return sample_id # TODO

    # @validator("repository_id")
    # def repository_id_exists(cls, repository_id):
    #     return repository_id # TODO
