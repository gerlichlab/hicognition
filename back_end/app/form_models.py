"""Pydantic models to validate integrity of Forms for the HiCognition API."""
import json
from typing import Any, Optional
from pydantic import BaseModel, Field, validator, constr, AnyHttpUrl, Json
from flask import current_app


class DatasetModel(BaseModel):
    """Base pydantic form model for dataset.
    Allows for additional fields using a metadata json.
    """

    def __init__(self, **data: Any) -> None:
        # temporary until metadata is resolved
        metadata_json = json.loads(data.get("metadata_json", "{}"))
        metadata_update_dict = {
            key: value
            for key, value in metadata_json.items()
            if key in current_app.config["METADATA_KEYS"]
        }
        data.update(metadata_update_dict)
        super().__init__(**data)

    class Config(BaseModel.Config):
        allow_population_by_field_name = True
        extra = "forbid"

    # TODO add checks for correct metadata

    def __getitem__(self, item):
        if hasattr(self, item):
            return getattr(self, item)
        return getattr(self, self.get_reverse_alias(item))

    def __contains__(self, item):
        return hasattr(self, item)


class DatasetPutModel(DatasetModel):
    """Is a model of the dataset modify form."""

    dataset_name: Optional[constr(min_length=3, max_length=81)] = Field(
        alias="datasetName"
    )
    public: Optional[bool] = Field(alias="Public")
    description: Optional[constr(max_length=81)] = Field(alias="Description")
    perturbation: Optional[constr(max_length=64)] = Field(alias="Perturbation")
    cellCycleStage: Optional[constr(max_length=64)] = Field(alias="Cell cycle Stage")
    method: Optional[constr(max_length=64)] = Field(alias="Method")
    normalization: Optional[constr(max_length=64)] = Field(alias="Normalization")
    derivationType: Optional[constr(max_length=64)] = Field(alias="DerivationType")
    protein: Optional[constr(max_length=64)] = Field(alias="Protein")
    directionality: Optional[constr(max_length=64)] = Field(alias="Directionality")
    valueType: Optional[constr(max_length=64)] = Field(alias="ValueType")
    metadata_json: Optional[Json[Any]]


# pylint: disable=no-self-argument,no-self-use
class DatasetPostModel(DatasetModel):
    """Is a model of the dataset upload form."""

    def __init__(__pydantic_self__, **data: Any) -> None:
        # remove empty fields
        data = {
            key: value
            for key, value in data.items()
            if value is not None and value.strip() != ""
        }
        if "sizeType" not in data and "SizeType" not in data:
            data["sizeType"] = ""
        super().__init__(**data)

    dataset_name: constr(min_length=3, max_length=81) = Field(...)
    public: bool = Field(...)
    assembly: int = Field(..., alias="assembly")
    description: str = Field("No description provided", max_length=81)
    # dataset_type: DatasetTypeEnum = Field(...)
    # size_type: SizeTypeEnum = Field(alias="SizeType")
    filetype: str = Field(..., max_length=64, alias="filetype")
    sizeType: str = Field(..., alias="SizeType")
    metadata_json: Json[Any] = Field(default={})

    perturbation: Optional[constr(max_length=64)] = Field(alias="Perturbation")
    cellCycleStage: Optional[constr(max_length=64)] = Field(alias="Cell cycle Stage")
    valueType: Optional[constr(max_length=64)] = Field(alias="ValueType")
    method: Optional[constr(max_length=64)] = Field(alias="Method")
    normalization: Optional[constr(max_length=64)] = Field(alias="Normalization")
    derivationType: Optional[constr(max_length=64)] = Field(alias="DerivationType")
    protein: Optional[constr(max_length=64)] = Field(alias="Protein")
    directionality: Optional[constr(max_length=64)] = Field(alias="Directionality")

    @validator("filetype")
    def check_filetype(cls, filetype, values, **kwargs):
        allowed_file_types = current_app.config["FILETYPES"]
        if not filetype:
            raise ValueError(
                f"Filetype is required! Supported: {allowed_file_types.keys()}."
            )
        if filetype not in allowed_file_types:
            raise ValueError(
                f"Unsupported filetype! We do not support following filetype: {filetype}. Supported: {allowed_file_types.keys()}."
            )
        return filetype

    @validator("sizeType")
    def check_sizeType(cls, sizeType, values, **kwargs):
        if "filetype" not in values:
            raise ValueError("File type is missing.")

        is_region = "region" in current_app.config["FILETYPES"].get(
            values["filetype"], {}
        ).get("dataset_type", [])
        has_sizeType = sizeType and sizeType.strip() != ""
        if has_sizeType and is_region:
            return sizeType

        if has_sizeType and not is_region:
            raise ValueError(
                f"sizeType only allowed for regions. {values['filetype']} is a feature"
            )
        if is_region and not has_sizeType:
            raise ValueError(f"sizeType required for regions.")
        return None

    # @validator("description")
    # def parse_description(cls, description):
    #     """Checks if description was provided provided in frontend, if not rewrites it."""
    #     if not description or description == "null" or description == '':
    #         description = "No description provided"
    #     return description


class FileDatasetPostModel(DatasetPostModel):
    """model of dataset with file"""

    filename: constr(max_length=200) = Field(...)

    @validator("filename")
    def check_filename(cls, filename, values, **kwargs):
        """Checks if file is correct, removes gz from compressed files"""
        if "filetype" not in values:
            raise ValueError("Invalid filename! File type is missing.")

        temp_filename = filename
        if temp_filename.lower().endswith(".gz"):
            temp_filename = temp_filename[:-3]

        file_ext = temp_filename[temp_filename.rindex(".") + 1 :]
        file_extensions = (
            current_app.config["FILETYPES"]
            .get(values["filetype"], {})
            .get("file_ext", [])
        )

        if file_ext not in file_extensions:
            raise ValueError(
                f"File extension {file_ext} not allowed. Allowed: {file_extensions}"
            )

        return filename


class URLDatasetPostModel(DatasetPostModel):
    """model of dataset with an URL"""

    source_url: AnyHttpUrl = Field(...)


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
