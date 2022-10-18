"""Pydantic models to validate integrity of Forms for the HiCognition API."""
from pydantic import BaseModel, Field, validator, constr, AnyUrl

from flask import current_app
from .utils import convert_format, Format

class DatasetMetadataModel(BaseModel):
    
    
    class Config:
        orm_mode = True

# pylint: disable=no-self-argument,no-self-use
class DatasetPostModel(BaseModel):
    """Is a model of the dataset upload form."""

    dataset_name: constr(min_length=3, max_length=81)
    public: bool
    assembly: int
    description: constr(max_length=81) = Field("No description provided")
    filetype: constr(max_length=64)
    sizeType: constr(max_length=64)
    filetype: constr(max_length=64)
    value_type: constr(max_length=64)

    dataset_metadata: list[DatasetMetadataModel]
    # def __init__(self, form: dict, **data):
    #     form = convert_format(form, Format.SNAKE_CASE)
    #     super.__init__(self, **data)

    class Config(BaseModel.Config):
        allow_population_by_field_name = True
        extra = "allow"

    @validator("filetype")
    def check_filetype(cls, filetype, values, **kwargs):
        allowed_file_types = current_app.config["FILETYPES"]
        if not filetype:
            raise ValueError(
                f"Filetype is required! Supported filestypes and endings are: {allowed_file_types.keys()}."
            )
        if filetype not in allowed_file_types:
            raise ValueError(
                f"Unsupported filetype! We do not support following filetype: {filetype}. Supported filestypes and endings are: {allowed_file_types.keys()}."
            )
        return filetype

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

    # @validator("filename")
    # def file_has_correct_ending_and_supported_filetype(cls, filename, values, **kwargs):
    #     """Checks is the file has the appropriate file ending."""
    #     supported_file_endings = current_app.config["DATASET_OPTION_MAPPING"][
    #         "supported_file_endings"
    #     ]
    #     file_ending = filename.split(".")[-1]
    #     if file_ending.lower() not in supported_file_endings.get(
    #         values.get("filetype")
    #     ):
    #         raise ValueError(
    #             f'Invalid filename! For the filetype: {values.get("filetype")} we found the file ending: {file_ending}. Supported for this filetype are: {supported_file_endings.get(values.get("filetype"))}.'
    #         )
    #     return filename


class URLDatasetPostModel(DatasetPostModel):
    """model of dataset with an URL"""

    source_url: AnyUrl


class ENCODEDatasetPostModel(DatasetPostModel):
    """model of dataset with an URL"""

    sample_id: constr(max_length=128)
    repository_name: constr(max_length=64)

    # @validator("sample_id")
    # def sample_id_exists(cls, sample_id):
    #     return sample_id # TODO

    # @validator("repository_id")
    # def repository_id_exists(cls, repository_id):
    #     return repository_id # TODO
