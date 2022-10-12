"""API endpoints for hicognition"""
import logging
import os
import json
import pandas as pd
import cooler
import numpy as np
from werkzeug.utils import secure_filename
from flask import g, request, current_app
from flask.json import jsonify

# from hicognition.utils import get_all_interval_ids, parse_binsizes
from hicognition.utils import parse_description, get_all_interval_ids, parse_binsizes
from hicognition.format_checkers import FORMAT_CHECKERS
from . import api
from .. import db

from .. import download_utils

from ..models import (
    Assembly,
    DataRepository,
    Dataset,
    BedFileMetadata,
    Organism,
    Session,
    Intervals,
    Collection,
    EmbeddingIntervalData,
)
from ..form_models import (
    DatasetPostModel,
    FileDatasetPostModel,
    URLDatasetPostModel,
    ENCODEDatasetPostModel,
)
from .authentication import auth
from .. import pipeline_steps
from .errors import forbidden, internal_server_error, invalid, not_found


@api.route("/datasets/encode/", methods=["POST"])
@auth.login_required
def add_dataset_from_ENCODE():
    """Endpoint to add dataset directly from an ENCODE repository.
    Will call new redis worker to download file and notify user when finished."""

    def is_form_valid():
        valid = True
        valid = valid and hasattr(request, "form")
        valid = valid and len(request.files) == 0
        return valid

    if not is_form_valid():
        return invalid("Form is not valid!")

    # get data from form
    try:
        data = ENCODEDatasetPostModel(**request.form)
    except ValueError as err:
        return invalid(f'Form is not valid: {str(err)}')
    except Exception as err:
        return internal_server_error(
            err,
            "Dataset could not be uploaded: There was a server-side error. Error has been logged.",
        )

    # temporary file_type check
    if data.filetype.lower() in ["cool", "cooler", "mcool"]:
        return invalid(
            f"Extern import of files with filetype '{data['filetype']}' not yet supported"
        )

    repository = db.session.query(DataRepository).get(data.repository_name)
    if not repository:
        return invalid(f"Repository {data.repository_name} not found.")

    # check if the sample exists:
    try:
        response = download_utils.download_ENCODE_metadata(repository, data.sample_id)
    except download_utils.MetadataNotWellformed as err:
        return invalid(f"Could not load metadata: {str(err)}")

    # check whether description is there
    description = parse_description(data)
    # check whether dataset should be public
    set_public = "public" in data and data["public"] == True
    # add data to Database -> in order to get id for filename
    new_entry = Dataset(
        dataset_name=data.dataset_name,
        description=description,
        public=set_public,
        processing_state="uploading",
        filetype=data.filetype,
        user_id=g.current_user.id,
        repository_name=data.repository_name,
        sample_id=data.sample_id,
    )
    new_entry.add_fields_from_form(data)
    db.session.add(new_entry)
    db.session.commit()

    g.current_user.launch_task(
        current_app.queues["short"],
        "download_dataset_file",
        "run dataset download from repo",
        new_entry.id,
    )
    return jsonify({"message": "success! File is being downloaded."})


@api.route("/datasets/URL/", methods=["POST"])
@auth.login_required
def add_dataset_from_URL():
    """Endpoint to add dataset with file provided by URL.
    Will call new redis worker to download file and notify user when finished."""

    def is_form_valid():
        valid = True
        valid = valid and hasattr(request, "form")
        valid = valid and len(request.files) == 0
        return valid

    if not is_form_valid():
        return invalid("Form is not valid!")

    # get data from form
    try:
        data = URLDatasetPostModel(**request.form)
    except ValueError as err:
        return invalid(f'"Form is not valid: {str(err)}')
    except Exception as err:
        return internal_server_error(
            err,
            "Dataset could not be uploaded: There was a server-side error. Error has been logged.",
        )

    # temporary file_type check
    if data.filetype.lower() in ["cool", "cooler", "mcool"]:
        return invalid(
            f"Extern import of files with filetype '{data['filetype']}' not yet supported"
        )

    # check whether description is there
    description = parse_description(data)
    # add data to Database -> in order to get id for filename
    new_entry = Dataset(
        dataset_name=data.dataset_name,
        description=description,
        public=data.public,
        processing_state="uploading",
        filetype=data.filetype,
        user_id=g.current_user.id,
        source_url=data.source_url,
    )
    new_entry.add_fields_from_form(data)
    db.session.add(new_entry)
    db.session.commit()

    g.current_user.launch_task(
        current_app.queues["short"],
        "download_dataset_file",
        "run dataset download from repo",
        new_entry.id,
    )
    return jsonify({"message": "success! File is being downloaded."})


@api.route("/datasets/", methods=["POST"])
@auth.login_required
def add_dataset():
    """endpoint to add a new dataset"""

    def is_form_invalid():
        invalid = False
        invalid = invalid or not hasattr(request, "form")
        invalid = invalid or len(request.files) == 0
        return invalid

    current_user = g.current_user
    # check form
    if is_form_invalid():
        return invalid("Form is not valid!")
    # get data from form
    try:
        data = FileDatasetPostModel(
            **request.form, filename=request.files["file"].filename
        )
    except ValueError as err:
        return invalid(f'"Form is not valid: {str(err)}')
    except Exception as err:
        return internal_server_error(
            err,
            "Dataset could not be uploaded: There was a server-side error. Error has been logged.",
        )

    # check whether description is there
    description = parse_description(data)
    # check whether dataset should be public
    set_public = "public" in data and data["public"] == True
    # add data to Database -> in order to get id for filename
    new_entry = Dataset(
        dataset_name=data.dataset_name,
        description=description,
        public=set_public,
        processing_state="uploading",
        filetype=data.filetype,
        user_id=current_user.id,
    )
    new_entry.add_fields_from_form(data)
    db.session.add(new_entry)
    db.session.commit()

    # save file in upload directory with database_id as prefix
    file_object = request.files["file"]
    filename = f"{new_entry.id}_{secure_filename(file_object.filename)}"
    file_path = os.path.join(current_app.config["UPLOAD_DIR"], filename)
    file_object.save(file_path)
    new_entry.file_path = file_path
    new_entry.processing_state = "uploaded"

    # validate dataset and delete if not valid
    if not new_entry.validate_dataset(delete=True):
        return invalid("Wrong dataformat or wrong chromosome names!")

    new_entry.preprocess_dataset()
    db.session.commit()
    return jsonify(
        {"message": "success! File is handed in for preprocessing."}
    )  # TODO preprocessing ambiguous


@api.route("/preprocess/datasets/", methods=["POST"])
@auth.login_required
def preprocess_dataset():
    """Starts preprocessing pipeline
    for datasets specified in the request body"""

    def is_form_invalid():
        if not hasattr(request, "form"):
            return True
        if sorted(list(request.form.keys())) != sorted(
            ["dataset_ids", "region_ids", "preprocessing_map"]
        ):
            return True
        return False

    current_user = g.current_user
    # check form
    if is_form_invalid():
        return invalid("Form is not valid!")
    # get data from form
    data = request.form
    dataset_ids = json.loads(data["dataset_ids"])
    region_datasets_ids = json.loads(data["region_ids"])
    preprocessing_map_type = data["preprocessing_map"]
    # check whether preprocessing map exists
    if preprocessing_map_type not in current_app.config:
        return invalid("Preprocessing map does not exist!")
    # assign preprocessing map
    preprocessing_map = current_app.config[preprocessing_map_type]
    # check whether datasets exist
    feature_datasets = [Dataset.query.get(feature_id) for feature_id in dataset_ids]
    if any(entry is None for entry in feature_datasets):
        return not_found("Dataset does not exist!")
    if any(entry.is_access_denied(g) for entry in feature_datasets):
        return forbidden("Dataset is not owned by logged in user!")
    # check whether region datasets exists
    region_datasets = [
        Dataset.query.get(region_id) for region_id in region_datasets_ids
    ]
    if any(entry is None for entry in region_datasets):
        return not_found("Region dataset does not exist!")
    # check whether region datasets are owned
    if any(entry.is_access_denied(g) for entry in region_datasets):
        return forbidden("Dataset is not owned by logged in user!")
    # delete all jobs that are in database and have failed and remove failed entries
    for dataset in feature_datasets:
        for region_ds in region_datasets:
            # change failed entries
            region_ds.failed_features = [
                feature for feature in region_ds.failed_features if feature != dataset
            ]
            # remove associated tasks
            dataset.remove_failed_tasks_for_region(db, region_ds)
    # check whether all intervals exist and create missing ones
    for region_dataset in region_datasets:
        missing_windowsizes = region_dataset.get_missing_windowsizes(preprocessing_map)
        for missing_windowsize in missing_windowsizes:
            pipeline_steps.bed_preprocess_pipeline_step(
                region_dataset.id, missing_windowsize
            )
    # get interval ids of selected regions
    interval_ids = get_all_interval_ids(region_datasets)
    # dispatch appropriate pipelines
    for interval_id in interval_ids:
        windowsize = Intervals.query.get(interval_id).windowsize
        if windowsize is None:
            windowsize = "variable"
        # check whether windowsize is in preprocessing map
        if windowsize not in preprocessing_map:
            continue
        for binsize in preprocessing_map[windowsize][dataset.filetype]:
            for dataset in feature_datasets:
                current_user.launch_task(
                    current_app.queues[
                        current_app.config["PIPELINE_QUEUES"][dataset.filetype]
                    ],
                    *current_app.config["PIPELINE_NAMES"][dataset.filetype],
                    dataset.id,
                    intervals_id=interval_id,
                    binsize=binsize,
                )
                if (
                    Intervals.query.get(interval_id).source_dataset
                    not in dataset.processing_regions
                ):
                    dataset.processing_regions.append(
                        Intervals.query.get(interval_id).source_dataset
                    )
    db.session.commit()
    return jsonify({"message": "success! Preprocessing triggered."})


@api.route("/preprocess/collections/", methods=["POST"])
@auth.login_required
def preprocess_collections():
    """Starts preprocessing pipeline
    for collections specified in the request body"""

    def is_form_invalid():
        if not hasattr(request, "form"):
            return True
        if sorted(list(request.form.keys())) != sorted(
            ["collection_ids", "region_ids", "preprocessing_map"]
        ):
            return True
        return False

    current_user = g.current_user
    # check form
    if is_form_invalid():
        return invalid("Form is not valid!")
    # get data from form
    data = request.form
    collection_ids = json.loads(data["collection_ids"])
    region_datasets_ids = json.loads(data["region_ids"])
    preprocessing_map_type = data["preprocessing_map"]
    # check whether preprocessing map exists
    if preprocessing_map_type not in current_app.config:
        return invalid("Preprocessing map does not exist!")
    # assign preprocessing map
    preprocessing_map = current_app.config[preprocessing_map_type]
    # check whether collection exists
    collections = [
        Collection.query.get(collection_id) for collection_id in collection_ids
    ]
    if any(entry is None for entry in collections):
        return not_found("Collection does not exist!")
    if any(collection.is_access_denied(g) for collection in collections):
        return forbidden("Collection is not owned by logged in user!")
    # check whether region datasets exists
    region_datasets = [
        Dataset.query.get(region_id) for region_id in region_datasets_ids
    ]
    if any(entry is None for entry in region_datasets):
        return not_found("Region dataset does not exist!")
    # check whether region datasets are owned
    if any(entry.is_access_denied(g) for entry in region_datasets):
        return forbidden("Region dataset is not owned by logged in user!")
    # delete all jobs that are in database and have failed
    for collection in collections:
        for region_ds in region_datasets:
            # change failed entries
            region_ds.failed_collections = [
                candidate
                for candidate in region_ds.failed_collections
                if candidate != collection
            ]
            collection.remove_failed_tasks_for_region(db, region_ds)
    # check whether all intervals exist and create missing ones
    for region_dataset in region_datasets:
        missing_windowsizes = region_dataset.get_missing_windowsizes(preprocessing_map)
        for missing_windowsize in missing_windowsizes:
            pipeline_steps.bed_preprocess_pipeline_step(
                region_dataset.id, missing_windowsize
            )
    # get interval ids of selected regions
    interval_ids = get_all_interval_ids(region_datasets)
    # dispatch appropriate pipelines
    for interval_id in interval_ids:
        windowsize = Intervals.query.get(interval_id).windowsize
        if windowsize is None:
            windowsize = "variable"
        # check whether windowsize is in preprocessing map
        if windowsize not in preprocessing_map:
            continue
        for binsize in preprocessing_map[windowsize]["collections"][collection.kind]:
            for collection in collections:
                current_user.launch_collection_task(
                    current_app.queues[
                        current_app.config["PIPELINE_QUEUES"]["collections"][
                            collection.kind
                        ]
                    ],
                    *current_app.config["PIPELINE_NAMES"]["collections"][
                        collection.kind
                    ],
                    collection.id,
                    intervals_id=interval_id,
                    binsize=binsize,
                )
                if (
                    Intervals.query.get(interval_id).source_dataset
                    not in collection.processing_for_datasets
                ):
                    collection.processing_for_datasets.append(
                        Intervals.query.get(interval_id).source_dataset
                    )
    db.session.commit()
    return jsonify({"message": "success! Preprocessing triggered."})


@api.route("/bedFileMetadata/", methods=["POST"])
@auth.login_required
def add_bedfile_metadata():
    """Add metadata file to metadata table.
    If uploaded metadatafile has different row-number than original bedfile ->
    return error."""

    SEPARATOR_MAP = {",": ",", ";": ";", "tab": "\t"}

    def is_form_invalid():
        if not hasattr(request, "form"):
            return True
        # check attributes
        if "datasetID" not in request.form.keys():
            return True
        if "separator" not in request.form.keys():
            return True
        # check whether fileObject is there
        if len(request.files) == 0:
            return True
        # check filename
        file_ending = request.files["file"].filename.split(".")[-1]
        correct_file_endings = ["csv", "txt", "bed"]  # textfiles and bedfiles supported
        if file_ending not in correct_file_endings:
            return True
        return False

    # check form
    if is_form_invalid():
        return invalid("Form is not valid!")
    # get data from form
    data = request.form
    file_object = request.files["file"]
    dataset_id = json.loads(data["datasetID"])
    # check whether dataset exists and user is allowed to access
    if Dataset.query.get(dataset_id) is None:
        return not_found("Dataset does not exist!")
    if Dataset.query.get(dataset_id).is_access_denied(g):
        return forbidden("Dataset is not owned by logged in user!")
    # check whether row-number is correct
    dataset = Dataset.query.get(dataset_id)
    dataset_file = pd.read_csv(
        dataset.file_path, sep="\t", header=None
    )  # during upload process, the header of bedfiles is removed
    uploaded_file = pd.read_csv(
        file_object, sep=SEPARATOR_MAP[data["separator"]]
    )  # generate uploaded dataframe from io-stream in memory
    if len(dataset_file) != len(uploaded_file):
        return jsonify({"ValidationError": "Dataset length missmatch!"})
    # detect numeric columns
    only_numeric = uploaded_file.select_dtypes(include=np.number)
    # save with standard separator
    filename = secure_filename(file_object.filename)
    file_path = os.path.join(current_app.config["UPLOAD_DIR"], filename)
    only_numeric.to_csv(file_path, index=False)
    # add to database
    new_metadata = BedFileMetadata(
        name=file_path.split(os.sep)[-1], file_path=file_path, dataset_id=dataset_id
    )
    db.session.add(new_metadata)
    db.session.commit()
    # return field_names to include for metadata
    return jsonify(
        {
            "message": "success! Preprocessing triggered.",
            "field_names": list(sorted(only_numeric.columns)),
            "id": new_metadata.id,
        }
    )


@api.route("/bedFileMetadata/<metadata_id>/setFields", methods=["POST"])
@auth.login_required
def add_bedfile_metadata_fields(metadata_id):
    """Add relevant metadatafields of the corresponding metadatafile."""

    def is_form_invalid():
        if not hasattr(request, "form"):
            return True
        # check attributes
        if "fields" not in request.form.keys():
            return True
        return False

    # check form
    if is_form_invalid():
        return invalid("Form is not valid!")
    # get data from form
    data = request.form
    field_map = json.loads(data["fields"])
    # check whether dataset exists and user is allowed to access
    if BedFileMetadata.query.get(metadata_id) is None:
        return not_found("Metadataset does not exist!")
    if BedFileMetadata.query.get(metadata_id).associated_dataset.is_access_denied(g):
        return forbidden("Associated dataset is not owned by logged in user!")
    # check whether field_names are correct
    metadata = BedFileMetadata.query.get(metadata_id)
    metadata_file = pd.read_csv(metadata.file_path)
    if not all(key in metadata_file.columns for key in field_map):
        return invalid("Field names not understood!")
    # store field_map in database
    metadata.metadata_fields = json.dumps(field_map)
    db.session.commit()
    return jsonify({"message": "Success! Field map added."})


@api.route("/sessions/", methods=["POST"])
@auth.login_required
def create_session():
    """Creates a session with name."""

    def is_form_invalid():
        if not hasattr(request, "form"):
            return True
        if len(request.form) == 0:
            return True
        # check attributes
        if sorted(request.form.keys()) != [
            "name",
            "session_object",
            "session_type",
            "used_collections",
            "used_datasets",
        ]:
            return True
        return False

    # check form
    if is_form_invalid():
        return invalid("Form is not valid!")
    # get data from form
    data = request.form
    name = data["name"]
    session_object = data["session_object"]
    session_type = data["session_type"]
    used_datasets = json.loads(data["used_datasets"])
    used_collections = json.loads(data["used_collections"])
    # check whether datasets exist
    datasets = [Dataset.query.get(dataset_id) for dataset_id in used_datasets]
    if any(dataset is None for dataset in datasets):
        return invalid("Some of the datasets in used_datasets do not exist!")
    # check whether dataset is owned or session token is valid
    if any(dataset.is_access_denied(g) for dataset in datasets):
        return forbidden(
            "Some of the datasets associated with this session are not owned!"
        )
    # check whether collections exist
    collections = [
        Collection.query.get(collection_id) for collection_id in used_collections
    ]
    if any(collection is None for collection in collections):
        return invalid("Some of the collections in used_collections do not exist!")
    if any(collection.is_access_denied(g) for collection in collections):
        return forbidden(
            "Some of the collections associated with this session are not owned!"
        )
    # create session
    session = Session(
        user_id=g.current_user.id,
        name=name,
        session_object=session_object,
        session_type=session_type,
        datasets=datasets,
        collections=collections,
    )
    db.session.add(session)
    db.session.commit()
    return jsonify({"session_id": f"{session.id}"})


@api.route("/collections/", methods=["POST"])
@auth.login_required
def create_collection():
    """Creates a dataset collection"""

    def is_form_invalid():
        if not hasattr(request, "form"):
            return True
        if len(request.form) == 0:
            return True
        # check attributes
        if sorted(request.form.keys()) != ["kind", "name", "used_datasets"]:
            return True
        return False

    # check form
    if is_form_invalid():
        return invalid("Form is not valid!")
    # get data from form
    data = request.form
    name = data["name"]
    used_datasets = json.loads(data["used_datasets"])
    kind = data["kind"]
    # check whether datasets exist
    datasets = [Dataset.query.get(dataset_id) for dataset_id in used_datasets]
    if any(dataset is None for dataset in datasets):
        return invalid("Some of the datasets in used_datasets do not exist!")
    # check whether dataset is owned or session token is valid
    if any(dataset.is_access_denied(g) for dataset in datasets):
        return forbidden(
            "Some of the datasets associated with this collection are not owned!"
        )
    # create collection
    collection = Collection(user_id=g.current_user.id, name=name, kind=kind)
    # add datasets
    collection.datasets.extend(datasets)
    db.session.add(collection)
    db.session.commit()
    return jsonify({"collection_id": f"{collection.id}"})


@api.route("/assemblies/", methods=["POST"])
@auth.login_required
def create_assembly():
    """Creates a genome assembly."""

    def is_form_invalid():
        if not hasattr(request, "form"):
            return True
        if len(request.form) == 0:
            return True
        # check whether fileObject is there
        if sorted(request.files.keys()) != ["chromArms", "chromSizes"]:
            return True
        # check attributes
        if sorted(request.form.keys()) != ["name", "organism"]:
            return True
        # check whether organism exists
        if Organism.query.get(int(request.form["organism"])) is None:
            return True
        return False

    # check form
    if is_form_invalid():
        return invalid("Form is not valid!")
    # get data from form
    data = request.form
    chrom_sizes = request.files["chromSizes"]
    chrom_arms = request.files["chromArms"]
    # add data to Database -> needed to obtain next id for filename
    new_entry = Assembly(
        name=data["name"], organism_id=int(data["organism"]), user_id=g.current_user.id
    )
    db.session.add(new_entry)
    db.session.commit()
    # save file in upload folder
    chrom_sizes_path = os.path.join(
        current_app.config["UPLOAD_DIR"],
        f"{new_entry.id}_{secure_filename(chrom_sizes.filename)}",
    )
    chrom_sizes.save(chrom_sizes_path)
    chrom_arms_path = os.path.join(
        current_app.config["UPLOAD_DIR"],
        f"{new_entry.id}_{secure_filename(chrom_arms.filename)}",
    )
    chrom_arms.save(chrom_arms_path)
    # check formats
    if (not FORMAT_CHECKERS["chromsizes"](chrom_sizes_path)) or (
        not FORMAT_CHECKERS["chromarms"](chrom_arms_path)
    ):
        db.session.delete(new_entry)
        db.session.commit()
        os.remove(chrom_sizes_path)
        os.remove(chrom_arms_path)
        return invalid("Wrong dataformat for chromosome sizes or chromosome arms!")
    # add file_paths to database entry
    new_entry.chrom_sizes = chrom_sizes_path
    new_entry.chrom_arms = chrom_arms_path
    db.session.add(new_entry)
    db.session.commit()
    return jsonify({"message": "success! Assembly added."})


@api.route("/embeddingIntervalData/<entry_id>/<cluster_id>/create/", methods=["POST"])
@auth.login_required
def create_region_from_cluster_id(entry_id, cluster_id):
    """Creates new region for cluster_id at entry_id"""

    def is_form_invalid():
        if not hasattr(request, "form"):
            return True
        if len(request.form) == 0:
            return True
        # check attributes
        if sorted(request.form.keys()) != ["name"]:
            return True
        return False

    # Check for existence
    if EmbeddingIntervalData.query.get(entry_id) is None:
        return not_found("Embedding data does not exist!")
    # Check whether datasets are owned
    embedding_data = EmbeddingIntervalData.query.get(entry_id)
    # Check whehter dataset/collections are owned
    if embedding_data.value_type == "1d-embedding":
        features = embedding_data.source_collection
    else:
        features = embedding_data.source_dataset
    bed_ds = embedding_data.source_intervals.source_dataset
    if features.is_access_denied(g) or bed_ds.is_access_denied(g):
        return forbidden(
            "Feature dataset or region dataset is not owned by logged in user!"
        )
    # check form
    if is_form_invalid():
        return invalid("Form is not valid!")
    # get data from form
    form_data = request.form
    # check whetehr thumbnails exist
    if embedding_data.cluster_id_path is None:
        return not_found("ClusterIDs do not exist")
    # load cluster ids
    cluster_ids = np.load(embedding_data.cluster_id_path).astype(int)
    # check whether cluster id is inside
    unique_ids = set(cluster_ids.astype(int))
    if int(cluster_id) not in unique_ids:
        return not_found("Cluster id does not exist!")
    # load regions
    regions = pd.read_csv(bed_ds.file_path, sep="\t", header=None)
    # create new dataset
    new_entry = Dataset(
        dataset_name=form_data["name"],
        description=bed_ds.description,
        public=False,  # derived regions are private by default - you can choose to make them public
        processing_state="uploading",
        filetype="bedfile",
        user_id=g.current_user.id,
    )
    # add fields
    new_entry.add_fields_from_dataset(bed_ds)
    db.session.add(new_entry)
    db.session.commit()
    # subset and write to file
    mask = cluster_ids == int(cluster_id)
    subset = regions.iloc[mask, :]
    filename = f"{new_entry.id}_subset_{bed_ds.dataset_name}"
    file_path = os.path.join(current_app.config["UPLOAD_DIR"], filename)
    subset.to_csv(file_path, sep="\t", header=None, index=False)
    # add file_path to database entry
    new_entry.file_path = file_path
    # start preprocessing for bedfile
    g.current_user.launch_task(
        current_app.queues["short"],
        "pipeline_bed",
        "run bed preprocessing",
        new_entry.id,
    )
    new_entry.processing_state = "processing"
    db.session.add(new_entry)
    db.session.commit()
    # return success
    return jsonify({"message": "success! Region subset"})
