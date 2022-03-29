from pydantic import BaseModel, Field, validator, constr
from flask import current_app


class DatasetPostModel(BaseModel):
    """Is a model of the dataset upload form."""

    dataset_name: constr(min_length=3, max_length=81) = Field(..., alias="datasetName")
    public: bool
    assembly: int  # TODO confirm name in upload tool
    description: constr(max_length=81) = Field("No description provided")
    normalization: constr(max_length=64) = Field(None, alias="Normalization")  #
    method: constr(max_length=64) = Field(..., alias="Method")
    size_type: constr(max_length=64) = Field(None, alias="SizeType")
    directionality: constr(max_length=64) = Field(None, alias="Directionality")  #
    derivation_type: constr(max_length=64) = Field(None, alias="DerivationType")  #
    protein: constr(max_length=64) = Field(None, alias="Protein")  #
    cell_cycle_stage: constr(max_length=64) = Field(..., alias="cellCycleStage")
    perturbation: constr(max_length=64)
    user_id: int = None  #
    processing_state: constr(max_length=64) = None  #
    filetype: constr(max_length=64)
    filename: constr(max_length=200)
    value_type: constr(max_length=64) = Field(..., alias="ValueType")

    class Config:
        """Sets up the alias generator"""

        allow_population_by_field_name = True
        extra = "forbid"

    @validator("value_type")
    def value_type_supported_in_dataset_attribute_mapping(
        cls, value_type, values, **kwargs
    ):
        """checks whether value_type passed dataset_attribute_mapping."""
        form_keys = set(cls.__dict__.keys())
        dataset_type_mapping = current_app.config["DATASET_OPTION_MAPPING"][
            "DatasetType"
        ]
        if values["filetype"] not in dataset_type_mapping.keys():
            raise ValueError(
                f'Unsupported filetype! We do not support following filetype: {values["filetype"]}. Supported filestypes are: {dataset_type_mapping.keys()}.'
            )
        value_types = dataset_type_mapping[values["filetype"]]["ValueType"]
        if value_type not in value_types.keys():
            raise ValueError(
                f'Unsupported value_type! We do not support value_type: {value_type} for the filetype {values["filetype"]}. We support {value_types.keys()}.'
            )
        # # check value type members
        # for key, possible_values in value_types[value_type].items():
        #     if key not in form_keys:
        #         raise ValueError(f'Unsupported possible value for value_type') #TODO what does this mean?
        #     # check whether field is freetext
        #     if possible_values == "freetext":
        #         continue
        #     # check that value in form corresponds to possible values
        #     if form[key] not in possible_values:
        #         raise ValueError(f'Unsupported possible value for value_type')
        return value_type

    @validator("filename")
    def file_has_correct_ending_and_supported_filetype(
        cls, filename, values, **kwargs
    ):  # TODO: Should this also be extracted from config?
        """Checks is the file has the appropriate file ending."""
        supported_file_endings = {
            "bedfile": ["bed"],
            "cooler": ["mcool"],
            "bigwig": ["bw", "bigwig"],
        }
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

    @validator("description")
    def parse_description(cls, description):
        if description == "null":
            description = "No description provided"
        return description

    def __getitem__(self, item):
        return getattr(self, item)

    def __contains__(self, item):
        return hasattr(self, item)



# @classmethod

# models.py line 398
# @classmethod
# def post_dataset_requirements_fullfilled(cls, form):
#     """checks whether form containing information to create dataset conforms
#     with the passed dataset_attribute_mapping."""
#     # check common things
#     form_keys = set(form.keys())
#     if any(key not in form_keys for key in cls.COMMON_REQUIRED_KEYS):
#         return False
#     if any(key not in form_keys for key in cls.ADD_REQUIRED_KEYS):
#         return False
#     # check metadata
#     dataset_type_mapping = current_app.config["DATASET_OPTION_MAPPING"]["DatasetType"]
#     value_types = dataset_type_mapping[form["filetype"]]["ValueType"]
#     if form["ValueType"] not in value_types.keys():
#         return False
#     # check value type members
#     for key, possible_values in value_types[form["ValueType"]].items():
#         if key not in form_keys:
#             return False
#         # check whether field is freetext
#         if possible_values == "freetext":
#             continue
#         # check that value in form corresponds to possible values
#         if form[key] not in possible_values:
#             return False
#     return True

