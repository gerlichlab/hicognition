"""Pydantic models to validate integrity of Forms for the HiCognition API."""
from enum import Enum
import json
from typing import Any, Optional
from pydantic import BaseModel, Field, validator, constr, AnyUrl, Json

from flask import current_app
from .utils import convert_format, Format

class SizeTypeEnum(str, Enum):
    point = 'point'
    interval = 'interval'

class DatasetTypeEnum(str, Enum):
    region = 'region'
    feature = 'feature'

# pylint: disable=no-self-argument,no-self-use
class DatasetPostModel(BaseModel):
    """Is a model of the dataset upload form."""
    
    def __init__(__pydantic_self__, **data: Any) -> None:
        # temporary until metadata is resolved
        metadata_json = json.loads(data.get('metadata_json', '{}'))
        for key in current_app.config['METADATA_KEYS']:
            data[key] = data.get(key, metadata_json.get(key, None))
        super().__init__(**data)
        

    dataset_name: constr(min_length=3, max_length=81) = Field(...)
    public: bool = Field(...)
    assembly: int = Field(...)
    description: constr(max_length=81) = Field("No description provided")
    dataset_type: DatasetTypeEnum = Field(...)
    sizeType: SizeTypeEnum = Field(...)
    filetype: constr(max_length=64) = Field("undefined")
    metadata_json: Json[Any]

    perturbation: Optional[constr(max_length=64)] = Field(alias="Perturbation")
    cellCycleStage: Optional[constr(max_length=64)] = Field(alias="Cell Cycle Stage")
    valueType: Optional[constr(max_length=64)] = Field(..., alias="ValueType")
    method: Optional[constr(max_length=64)] = Field(alias="Method")
    normalization: Optional[constr(max_length=64)] = Field(alias="Normalization")
    derivationType: Optional[constr(max_length=64)] = Field(alias="DerivationType")
    protein: Optional[constr(max_length=64)] = Field(alias="Protein")
    directionality: Optional[constr(max_length=64)] = Field(alias="Directionality")

    class Config(BaseModel.Config):
        allow_population_by_field_name = True

    @validator("sizeType")
    def require_size_type_region(cls, sizeType, values, **kwargs):
        if not sizeType and values['dataset_type'] == DatasetTypeEnum.region:
            raise ValueError("Size type required for regions.")

        if sizeType and values['dataset_type'] != DatasetTypeEnum.region:
            raise ValueError("Specifying size type only allowed for regions.")
        return sizeType

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
        if description == "null" or description == '':
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
    filename: constr(max_length=200) = Field(...)


class URLDatasetPostModel(DatasetPostModel):
    """model of dataset with an URL"""
    source_url: AnyUrl = Field(...)

    @validator("filetype")
    def check_filetype(cls, filetype, values, **kwargs):
        # temporary file_type check
        if filetype.lower() in ["cool", "cooler", "mcool"]:
            raise ValueError(
                f"Extern import of files with filetype '{filetype}' not yet supported"
            )
        return super().check_filetype(filetype, values, **kwargs)


class ENCODEDatasetPostModel(DatasetPostModel):
    """model of dataset with an URL"""
    sample_id: constr(max_length=128, min_length=3) = Field(...)
    repository_name: constr(max_length=128) = Field(...)
    
    @validator("filetype")
    def check_filetype(cls, filetype, values, **kwargs):
        # temporary file_type check
        if filetype.lower() in ["cool", "cooler", "mcool"]:
            raise ValueError(
                f"Extern import of files with filetype '{filetype}' not yet supported"
            )
        return super().check_filetype(filetype, values, **kwargs)

    # @validator("sample_id")
    # def validate_sample_id(cls, sample_id, values, **kwargs):
    #     if not sample_id or sample_id.strip() == '':
    #         raise ValueError("sample_id may not be empty")
    #     return sample_id