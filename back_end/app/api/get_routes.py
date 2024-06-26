"""GET API endpoints for hicognition"""
import json
import gzip
import logging
import pandas as pd
from requests import HTTPError, RequestException
import numpy as np
from flask import g, make_response
from flask.json import jsonify
from flask.globals import current_app
from ..lib import data_structures
from ..lib.utils import (
    update_processing_state,
    flatten_and_clean_array,
)
from . import api
from .. import db
from ..models import (
    BedFileMetadata,
    Repository,
    IntervalDataTypeEnum,
    Intervals,
    Dataset,
    AverageIntervalData,
    IndividualIntervalData,
    AssociationIntervalData,
    EmbeddingIntervalData,
    Session,
    Collection,
    Organism,
)
from .authentication import auth, check_confirmed
from .errors import forbidden, not_found, invalid
from ..download_utils import (
    DownloadUtilsException,
    download_ENCODE_metadata,
    MetadataNotWellformed,
)

# get logger
log = logging.getLogger("rq.worker")


@api.route("/test", methods=["GET"])
def test():
    """test api calls"""
    return jsonify({"test": "Hello, world!"})


@api.route("/testProtected", methods=["GET"])
@auth.login_required
def test_protected():
    """test api calls"""
    return jsonify({"test": "Hello, world!"})


# @api.route("/resolutions/", methods=["GET"])
# @auth.login_required
# @check_confirmed
# def get_resolutions():
#     """Gets available combinations of windowsizes and binsizes
#     from config file"""
#     return jsonify(current_app.config["PREPROCESSING_MAP"])


@api.route("/datasetMetadataMapping/", methods=["get"])
@auth.login_required
def get_metadata_mapping():
    """Get route for metadata mapping"""
    return jsonify(current_app.config["DATASET_OPTION_MAPPING"])


@api.route("/filetypes/", methods=["GET"])
@auth.login_required
def get_filetypes():
    """Returns filetype and associated metadata"""
    return jsonify(current_app.config["FILETYPES"])
    # file_types = current_app.config["FILETYPES"]
    #
    # if format == "snake_case":
    #     format = utils.Format.SNAKE_CASE
    # elif format == "camelCase":
    #     format = utils.Format.CAMELCASE
    # elif format == "human":
    #     format = utils.Format.HUMAN_READABLE

    # formatted_file_types = utils.convert_format(file_types, format)
    # return jsonify(formatted_file_types)


@api.route("/organisms/", methods=["GET"])
@auth.login_required
@check_confirmed
def get_organisms():
    """Get route for available organisms"""
    return jsonify([org.to_json() for org in Organism.query.all()])


@api.route("/assemblies/", methods=["GET"])
@auth.login_required
@check_confirmed
def get_assemblies():
    """Gets all assemblies in the database."""
    output = {}
    for organism in Organism.query.all():
        temp_list = []
        for assembly in organism.assemblies.all():
            temp_dict = assembly.to_json()
            temp_dict["dependent_datasets"] = len(
                Dataset.query.filter(Dataset.assembly == assembly.id).all()
            )
            temp_list.append(temp_dict)
        output[organism.name] = temp_list
    return output


@api.route("/datasets/", methods=["GET"])
@auth.login_required
@check_confirmed
def get_all_datasets():
    """Gets all available datasets for a given user."""
    all_available_datasets = Dataset.query.filter(
        (Dataset.user_id == g.current_user.id)
        | (Dataset.public)
        | (Dataset.id.in_(g.session_datasets))
        | current_app.config["SHOWCASE"]
    ).all()
    return jsonify([dfile.to_json() for dfile in all_available_datasets])


@api.route("/datasets/processing/", methods=["GET"])
@auth.login_required
@check_confirmed
def get_all_processing_datasets():
    """Gets all available datasets for a given user."""
    all_available_datasets = Dataset.query.filter(
        (Dataset.user_id == g.current_user.id)
        | (Dataset.public)
        | (Dataset.id.in_(g.session_datasets))
        | current_app.config["SHOWCASE"]
    ).all()
    # list processing datasets
    processing_datasets = [
        dataset
        for dataset in all_available_datasets
        if len(dataset.processing_features) != 0
        or len(dataset.processing_collections) != 0
        or dataset.upload_state in ["new", "uploading"]
    ]
    return jsonify([dfile.to_json() for dfile in processing_datasets])


@api.route("/datasets/<dtype>", methods=["GET"])
@auth.login_required
@check_confirmed
def get_datasets(dtype: str = ""):
    """Gets all available datasets for a given user."""
    if dtype == "cooler":
        cooler_files = Dataset.query.filter(
            (Dataset.filetype == "cooler")
            & ((g.current_user.id == Dataset.user_id) | (Dataset.public))
        ).all()
        update_processing_state(cooler_files, db)
        return jsonify([cfile.to_json() for cfile in cooler_files])
    if dtype == "bed":
        bed_files = Dataset.query.filter(
            (Dataset.filetype == "bedfile")
            & ((g.current_user.id == Dataset.user_id) | (Dataset.public))
        ).all()
        update_processing_state(bed_files, db)
        return jsonify([bfile.to_json() for bfile in bed_files])
    if dtype == "bigwig":
        bed_files = Dataset.query.filter(
            (Dataset.filetype == "bigwig")
            & ((g.current_user.id == Dataset.user_id) | (Dataset.public))
        ).all()
        update_processing_state(bed_files, db)
        return jsonify([bfile.to_json() for bfile in bed_files])
    return not_found(f"option: '{dtype}' not understood")


@api.route("/datasets/<dataset_id>/name/", methods=["GET"])
@auth.login_required
@check_confirmed
def get_name_of_dataset(dataset_id):
    """Returns the name for a given dataset, if the user owns the requested dataset."""
    dataset = Dataset.query.get(dataset_id)
    # check whether dataset exists
    if dataset is None:
        return not_found(f"Dataset with id '{dataset_id}' does not exist!")
    # check whether user owns the dataset
    if dataset.is_access_denied(g):
        return forbidden(
            f"Dataset with id '{dataset_id}' is not owned by logged in user!"
        )
    return jsonify(dataset.dataset_name)


@api.route("/datasets/<dataset_id>/bedFile/", methods=["GET"])
@auth.login_required
@check_confirmed
def get_dataset_file(dataset_id):
    """Returns the bedFile associate with a region dataset"""
    dataset = Dataset.query.get(dataset_id)
    # check whether dataset exists
    if dataset is None:
        return not_found(f"Dataset with id '{dataset_id}' does not exist!")
    # check whether user owns the dataset
    if dataset.is_access_denied(g):
        return forbidden(
            f"Dataset with id '{dataset_id}' is not owned by logged in user!"
        )
    # check whether the dataset is a bedfile
    if dataset.filetype != "bedfile":
        return invalid("Requested dataset is not a bedfile")
    # check whether file exists
    if dataset.file_path is None:
        return not_found("Dataset has not associated bedfile")
    # get bedfile
    data = pd.read_csv(dataset.file_path, sep="\t", header=None).iloc[:, :3]
    data.columns = ["chrom", "start", "end"]
    return data.to_json(orient="records")


@api.route("/datasets/<dataset_id>/processedDataMap/", methods=["GET"])
@auth.login_required
@check_confirmed
def get_processed_data_mapping_of_dataset(dataset_id):
    """Gets processed data map of a given region dataset.
    This object has the following structure:
    {
        processed_data_type: {
            associated_dataset_id/associated_collection_id: {
                name: NAME_OF_ASSOCIATED_DATASET/NAME_OF_ASSOCIATED_COLLECTION,
                (collection_dataset_names: [...names...],)
                data_ids: {
                    interval_size: {
                        binsize: {
                            processed_data_id
                        }
                    }
                }
            }
        }
    }

    Processed_data_type is in [pileup, stackup, lineprofile, lola, embedding1d, embedding2d]
    All entries for a given processed_data_type key are available processed_datasets.
    The values for each processed_dataset hold information about their name
    and which id in the target table corresponds to which interval and binsize
    combintaion.
    """
    dataset = Dataset.query.get(dataset_id)
    # check whether dataset exists
    if dataset is None:
        return not_found(f"Dataset with id '{dataset_id}' does not exist!")
    # check whether user owns the dataset
    if dataset.is_access_denied(g):
        return forbidden(
            f"Dataset with id '{dataset_id}' is not owned by logged in user!"
        )
    # check whether dataset is bedfile
    if dataset.filetype not in ["bedfile", "bedpefile"]:
        return invalid(f"Dataset with id '{dataset_id}' is not a bedfile!")
    # create output object
    output = {
        "pileup": data_structures.recDict(),
        "stackup": data_structures.recDict(),
        "lineprofile": data_structures.recDict(),
        "lola": data_structures.recDict(),
        "embedding1d": data_structures.recDict(),
        "embedding2d": data_structures.recDict(),
    }
    # populate output object #
    for interval in dataset.intervals:
        windows_size = (
            "variable" if dataset.sizeType == "Interval" else interval.windowsize
        )
        for ivd in interval.interval_data:
            if (  # TODO i don't like this
                (ivd.feature in ivd.source_intervals.source_dataset.processing_features)
                or (ivd.feature in ivd.source_intervals.source_dataset.failed_features)
                or (
                    ivd.feature
                    in ivd.source_intervals.source_dataset.processing_collections
                )
                or (
                    ivd.feature
                    in ivd.source_intervals.source_dataset.failed_collections
                )
            ):
                continue

            interval_datatype = ivd.intervaldata_type
            if interval_datatype == IntervalDataTypeEnum.EMBEDDING_1D.value:
                interval_datatype = "embedding1d"
            elif interval_datatype == IntervalDataTypeEnum.EMBEDDING_2D.value:
                interval_datatype = "embedding2d"

            # assigning name of feature
            feature_name = (
                ivd.feature.dataset_name
                if isinstance(ivd.feature, Dataset)
                else ivd.feature.name
            )
            output[interval_datatype][ivd.feature.id]["name"] = feature_name

            # assigning feature names if feature is a collection
            if isinstance(ivd.feature, Collection):
                output[interval_datatype][ivd.feature.id][
                    "collection_dataset_names"
                ] = ivd.feature.to_json()["dataset_names"]

            # assigning the id
            if isinstance(ivd, AverageIntervalData) and interval_datatype == "pileup":
                output[interval_datatype][ivd.feature.id]["data_ids"][windows_size][
                    ivd.binsize
                ][ivd.value_type] = str(ivd.id)
            elif (
                isinstance(ivd, AverageIntervalData)
                or isinstance(ivd, IndividualIntervalData)
            ) and ivd.region_side is not None:
                output[interval_datatype][ivd.feature.id]["data_ids"][windows_size][
                    ivd.binsize
                ][ivd.region_side] = str(ivd.id)
            elif (
                isinstance(ivd, EmbeddingIntervalData)
                and interval_datatype == "embedding1d"
            ):
                if ivd.region_side is not None:
                    output[interval_datatype][ivd.feature.id]["data_ids"][windows_size][
                        ivd.binsize
                    ][ivd.cluster_number][ivd.region_side] = str(ivd.id)
                else:
                    output[interval_datatype][ivd.feature.id]["data_ids"][windows_size][
                        ivd.binsize
                    ][ivd.cluster_number] = str(ivd.id)
            elif (
                isinstance(ivd, EmbeddingIntervalData)
                and interval_datatype == "embedding2d"
            ):
                output[interval_datatype][ivd.feature.id]["data_ids"][windows_size][
                    ivd.binsize
                ][ivd.normalization][ivd.cluster_number] = str(ivd.id)
            elif (
                isinstance(ivd, AssociationIntervalData) and ivd.region_side is not None
            ):
                output[interval_datatype][ivd.feature.id]["data_ids"][windows_size][
                    ivd.binsize
                ][ivd.region_side] = str(ivd.id)
            else:
                output[interval_datatype][ivd.feature.id]["data_ids"][windows_size][
                    ivd.binsize
                ] = str(ivd.id)

    return jsonify(output)


@api.route("/intervals/", methods=["GET"])
@auth.login_required
@check_confirmed
def get_intervals():
    """Gets all available intervals for a given user."""
    # SQL join to get all intervals that come from a dataset owned by the respective user
    all_files = (
        Intervals.query.join(Dataset)
        .filter(
            (Dataset.user_id == g.current_user.id)
            | (Dataset.public)
            | (Dataset.id.in_(g.session_datasets))
            | current_app.config["SHOWCASE"]
        )
        .all()
    )
    return jsonify([dfile.to_json() for dfile in all_files])


@api.route("/intervals/<interval_id>/metadata", methods=["GET"])
@auth.login_required
@check_confirmed
def get_interval_metadata(interval_id):
    """returns available metadata for given intervals."""
    interval = Intervals.query.get(interval_id)
    if interval is None:
        return not_found(f"Intervals with id {interval_id} do not exist!")
    # check if associated dataset is owned
    if interval.source_dataset.is_access_denied(g):
        return forbidden(
            f"Dataset associated with interval id {interval.id} is not owned by logged in user!"
        )
    # get associated metadata entries sorted by id in descending order
    # id sorting is necessary for newer metadata to win in field names
    metadata_entries = interval.source_dataset.bedFileMetadata.order_by(
        BedFileMetadata.id.desc()
    ).all()
    # check if list is empty
    if len(metadata_entries) == 0:
        return jsonify({})
    # load all metadata_files as dataframes
    temp_frames = []
    for metadata_entry in metadata_entries:
        if metadata_entry.metadata_fields is None:
            # skip metadata if there are no fields defined
            continue
        columns_retained = json.loads(metadata_entry.metadata_fields)
        temp_frame = pd.read_csv(metadata_entry.file_path, usecols=columns_retained)
        temp_frames.append(temp_frame)
    output_frame = pd.concat(temp_frames, axis=1)
    # this drops all occurrences of a given column but the first,
    # since ids are sorted by descending order, the newest one wins
    output_frame_unique = output_frame.loc[:, ~output_frame.columns.duplicated()]
    return jsonify(output_frame_unique.to_dict(orient="list"))


@api.route("/averageIntervalData/<entry_id>/", methods=["GET"])
@auth.login_required
@check_confirmed
def get_pileup_data(entry_id):
    """returns pileup data for the specified pileup id if it exists and
    access is allowed."""
    # Check for existence
    if AverageIntervalData.query.get(entry_id) is None:
        return not_found("Pileup does not exist!")
    # Check whether datasets are owned
    pileup = AverageIntervalData.query.get(entry_id)
    cooler_ds = pileup.source_dataset
    bed_ds = pileup.source_intervals.source_dataset
    if cooler_ds.is_access_denied(g) or bed_ds.is_access_denied(g):
        return forbidden(
            "Cooler dataset or bed dataset is not owned by logged in user!"
        )
    # Dataset is owned, return the data
    np_data = np.load(pileup.file_path)
    # Convert np.nan and np.isinf to None -> this is handeled by jsonify correctly
    flat_data = [
        entry if not (np.isnan(entry) or np.isinf(entry)) else None
        for entry in np_data.flatten()
    ]
    json_data = {"data": flat_data, "shape": np_data.shape, "dtype": "float32"}
    return jsonify(json_data)


@api.route("/associationIntervalData/<entry_id>/", methods=["GET"])
@auth.login_required
@check_confirmed
def get_association_data(entry_id):
    """returns data for the specified association data id if it exists and
    access is allowed."""
    # Check for existence
    if AssociationIntervalData.query.get(entry_id) is None:
        return not_found("Association data does not exist!")
    # Check whether datasets are owned
    association_data = AssociationIntervalData.query.get(entry_id)
    collection = association_data.source_collection
    bed_ds = association_data.source_intervals.source_dataset
    if collection.is_access_denied(g) or bed_ds.is_access_denied(g):
        return forbidden("Collection or bed dataset is not owned by logged in user!")
    # Dataset is owned, return the data
    np_data = np.load(association_data.file_path)
    # Convert np.nan and np.isinf to None -> this is handeled by jsonify correctly
    flat_data = [
        entry if not (np.isnan(entry) or np.isinf(entry)) else None
        for entry in np_data.flatten()
    ]
    json_data = {"data": flat_data, "shape": np_data.shape, "dtype": "float32"}
    return jsonify(json_data)


@api.route("/embeddingIntervalData/<entry_id>/", methods=["GET"])
@auth.login_required
@check_confirmed
def get_embedding_data(entry_id):
    """returns data for the specified embedding data id if it exists and
    access is allowed."""
    # Check for existence
    if EmbeddingIntervalData.query.get(entry_id) is None:
        return not_found("Embedding data does not exist!")
    # Check whether datasets are 1d or 2d
    embedding_data = EmbeddingIntervalData.query.get(entry_id)
    if embedding_data.value_type == "2d-embedding":
        # Check whether datasets are owned
        feature_dataset = embedding_data.source_dataset
        bed_ds = embedding_data.source_intervals.source_dataset
        if feature_dataset.is_access_denied(g) or bed_ds.is_access_denied(g):
            return forbidden(
                "Feature dataset or region dataset is not owned by logged in user!"
            )
        embedding = np.load(embedding_data.file_path).astype(float)
        cluster_ids = np.load(embedding_data.cluster_id_path).astype(float)
        thumbnails = np.load(embedding_data.thumbnail_path).astype(float)
        # Convert np.nan and np.isinf to None -> this is handeled by jsonify correctly
        json_data = {
            "embedding": {
                "data": flatten_and_clean_array(embedding),
                "shape": embedding.shape,
                "dtype": "float32",
            },
            "cluster_ids": {
                "data": flatten_and_clean_array(cluster_ids),
                "shape": cluster_ids.shape,
                "dtype": "float32",
            },
            "thumbnails": {
                "data": flatten_and_clean_array(thumbnails),
                "shape": thumbnails.shape,
                "dtype": "float32",
            },
        }
    else:
        # Check whether collections are owned
        collection = embedding_data.source_collection
        bed_ds = embedding_data.source_intervals.source_dataset
        if collection.is_access_denied(g) or bed_ds.is_access_denied(g):
            return forbidden(
                "Collection dataset or region dataset is not owned by logged in user!"
            )
        embedding = np.load(embedding_data.file_path).astype(float)
        if embedding_data.cluster_id_path is not None:
            cluster_ids = np.load(embedding_data.cluster_id_path).astype(float)
            average_data = np.load(embedding_data.thumbnail_path).astype(float)
            json_data = {
                "embedding": {
                    "data": flatten_and_clean_array(embedding),
                    "shape": embedding.shape,
                    "dtype": "float32",
                },
                "cluster_ids": {
                    "data": flatten_and_clean_array(cluster_ids),
                    "shape": cluster_ids.shape,
                    "dtype": "float32",
                },
                "thumbnails": {
                    "data": flatten_and_clean_array(average_data),
                    "shape": average_data.shape,
                    "dtype": "float32",
                },
            }
        else:
            json_data = {
                "embedding": {
                    "data": flatten_and_clean_array(embedding),
                    "shape": embedding.shape,
                    "dtype": "float32",
                },
                "cluster_ids": {
                    "data": None,
                    "shape": None,
                    "dtype": None,
                },
                "thumbnails": {
                    "data": None,
                    "shape": None,
                    "dtype": None,
                },
            }
    # compress
    content = gzip.compress(json.dumps(json_data).encode("utf8"), 4)
    response = make_response(content)
    response.headers["Content-length"] = len(content)
    response.headers["Content-Encoding"] = "gzip"
    return response


@api.route("/embeddingIntervalData/<entry_id>/<feature_index>/", methods=["GET"])
@auth.login_required
@check_confirmed
def get_embedding_feature(entry_id, feature_index):
    """Gets feature vector with feature_index for entry_id"""
    # Check for existence
    if EmbeddingIntervalData.query.get(entry_id) is None:
        return not_found("Embedding data does not exist!")
    # Check whether datasets are owned
    embedding_data = EmbeddingIntervalData.query.get(entry_id)
    collection = embedding_data.source_collection
    bed_ds = embedding_data.source_intervals.source_dataset
    if collection.is_access_denied(g) or bed_ds.is_access_denied(g):
        return forbidden("Collection or bed dataset is not owned by logged in user!")
    # return the feature data
    feature_data = np.load(embedding_data.file_path_feature_values, mmap_mode="r")
    selected_row = np.array(feature_data[:, int(feature_index)]).astype(np.float64)
    flat_data = [
        entry if not (np.isnan(entry) or np.isinf(entry)) else None
        for entry in selected_row.flatten()
    ]
    json_data = {"data": flat_data, "shape": selected_row.shape, "dtype": "float32"}
    # compress
    content = gzip.compress(json.dumps(json_data).encode("utf8"), 4)
    response = make_response(content)
    response.headers["Content-length"] = len(content)
    response.headers["Content-Encoding"] = "gzip"
    return response


@api.route("/individualIntervalData/<entry_id>/", methods=["GET"])
@auth.login_required
@check_confirmed
def get_stackup_data(entry_id):
    """returns stackup data for the specified stackup id if it exists and
    access is allowed."""
    # Check for existence
    if IndividualIntervalData.query.get(entry_id) is None:
        return not_found("Stackup does not exist!")
    stackup = IndividualIntervalData.query.get(entry_id)
    bigwig_ds = stackup.source_dataset
    bed_ds = stackup.source_intervals.source_dataset
    if bigwig_ds.is_access_denied(g) or bed_ds.is_access_denied(g):
        return forbidden(
            "Bigwig dataset or bed dataset is not owned by logged in user!"
        )
    # dataset is owned, return the smalldata
    np_data = np.load(stackup.file_path_small)
    # Convert np.nan and np.isinf to None -> this is handeled by jsonify correctly
    flat_data = [
        entry if not (np.isnan(entry) or np.isinf(entry)) else None
        for entry in np_data.flatten()
    ]
    json_data = {"data": flat_data, "shape": np_data.shape, "dtype": "float32"}
    return jsonify(json_data)


@api.route("/individualIntervalData/<entry_id>/metadatasmall", methods=["GET"])
@auth.login_required
@check_confirmed
def get_stackup_metadata_small(entry_id):
    """returns metadata for small stackup. This needs to be done since
    the subsampeled stackup contains only a subset of the original intervals.
    Note: stackups use the original dataset, so subsetting on interval indices
    is not required."""
    # Check for existence
    if IndividualIntervalData.query.get(entry_id) is None:
        return not_found("Stackup does not exist!")
    stackup = IndividualIntervalData.query.get(entry_id)
    # get downsample index from associated intervals
    down_sample_index = Intervals.query.get(
        stackup.intervals_id
    ).file_path_sub_sample_index
    bigwig_ds = stackup.source_dataset
    bed_ds = stackup.source_intervals.source_dataset
    if bigwig_ds.is_access_denied(g) or bed_ds.is_access_denied(g):
        return forbidden(
            "Bigwig dataset or bed dataset is not owned by logged in user!"
        )
    # get associated metadata entries sorted by id;
    # id sorting is necessary for newer metadata to win in field names
    metadata_entries = bed_ds.bedFileMetadata.order_by(BedFileMetadata.id.desc()).all()
    # check if list is empty or all metadata entries have undefined metadata fields
    if (len(metadata_entries) == 0) or all(
        metadata_entry.metadata_fields is None for metadata_entry in metadata_entries
    ):
        return jsonify({})
    # load all metadata_files as dataframes
    temp_frames = []
    for metadata_entry in metadata_entries:
        if metadata_entry.metadata_fields is None:
            # skip metadata if there are no fields defined
            continue
        columns_retained = json.loads(metadata_entry.metadata_fields)
        temp_frame = pd.read_csv(metadata_entry.file_path, usecols=columns_retained)
        temp_frames.append(temp_frame)
    output_frame_large = pd.concat(temp_frames, axis=1)
    # this drops all occurrences of a given column but the first,
    # since ids are sorted by descending order, the newest one wins
    output_frame_unique = output_frame_large.loc[
        :, ~output_frame_large.columns.duplicated()
    ]
    # subset by stackup index
    stackup_index = np.load(down_sample_index)
    outframe = output_frame_unique.iloc[stackup_index, :]
    return jsonify(outframe.to_dict(orient="list"))


@api.route("/sessions/", methods=["GET"])
@auth.login_required
@check_confirmed
def get_all_sessions():
    """Gets all available sessions for a given user."""
    all_available_sessions = Session.query.filter(
        (Session.user_id == g.current_user.id) | current_app.config["SHOWCASE"]
    ).all()
    return jsonify([dfile.to_json() for dfile in all_available_sessions])


@api.route("/sessions/<session_id>/", methods=["GET"])
@auth.login_required
@check_confirmed
def get_session_data_with_id(session_id):
    """Returns session data with given id"""
    # check whether session with id exists
    session = Session.query.get(session_id)
    # check whether dataset exists
    if session is None:
        return not_found(f"Session with id '{session_id}' does not exist!")
    # check if session is owned
    if (
        (session.user_id != g.current_user.id)
        and (session.id != g.session_id)
        and not current_app.config["SHOWCASE"]
    ):
        return forbidden(f"Session with id '{session_id}' is not owned!")
    return jsonify(session.to_json())


@api.route("/sessions/<session_id>/sessionToken/", methods=["GET"])
@auth.login_required
@check_confirmed
def get_session_token(session_id):
    """Returns session token for a given session."""
    # check whether session with id exists
    session = Session.query.get(session_id)
    # check whether dataset exists
    if session is None:
        return not_found(f"Session with id '{session_id}' does not exist!")
    # check if session is owned
    if (session.user_id != g.current_user.id) and not current_app.config["SHOWCASE"]:
        return forbidden(f"Session with id '{session_id}' is not owned!")
    # create session token
    return jsonify(
        {"session_token": session.generate_session_token(), "session_id": session_id}
    )


@api.route("/collections/", methods=["GET"])
@auth.login_required
@check_confirmed
def get_all_collections():
    """Gets all available collections for a given user."""
    all_available_collections = Collection.query.filter(
        (Collection.user_id == g.current_user.id)
        | Collection.public
        | (Collection.id.in_(g.session_collections))
        | current_app.config["SHOWCASE"]
    ).all()
    update_processing_state(all_available_collections, db)
    return jsonify([dfile.to_json() for dfile in all_available_collections])


@api.route("/repositories/", methods=["GET"])
@auth.login_required
@check_confirmed
def get_all_repositories():
    """Gets all repos in the db for file downloads"""
    repositories = db.session.query(Repository).all()
    return jsonify({repo.name: repo.to_json() for repo in repositories})


@api.route("/ENCODE/<repo_name>/<sample_id>/", methods=["GET"])
@auth.login_required
@check_confirmed
def get_ENCODE_metadata(repo_name: str, sample_id: str):
    """fetches metadata from an ENCODE repository about a file
    to auto-fill form when user wants import from it
    """
    repository = db.session.query(Repository).get(repo_name)
    if repository is None:
        return not_found(f"ENCODE repository {repo_name} not in our database.")

    try:
        data = download_ENCODE_metadata(repository, sample_id)
    except HTTPError as err:
        if err.response.status_code == 404:
            return jsonify(
                {
                    "status": "error",
                    "http_status_code": err.response.status_code,
                    "message": f"Could not find sample {sample_id}",
                }
            )
        if err.response.status_code == 403:
            return jsonify(
                {
                    "status": "error",
                    "http_status_code": err.response.status_code,
                    "message": f"Access forbidden by ENCODE repository",
                }
            )
        return invalid(
            f"Could not get metadata from server: {err.response.text}.  {str(err)}"
        )
    except (MetadataNotWellformed, DownloadUtilsException, RequestException) as err:
        return invalid(f"Could not get metadata from server: {str(err)}")

    return jsonify({"status": "ok", "http_status_code": 200, "json": data})
