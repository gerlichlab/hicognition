"""GET API endpoints for hicognition"""
import json
from flask.globals import current_app
import pandas as pd
import numpy as np
from flask.json import jsonify
from flask import g, request
from .helpers import (
    update_processing_state,
    is_access_to_dataset_denied,
    is_access_to_collection_denied,
    add_average_data_to_preprocessed_dataset_map,
    add_individual_data_to_preprocessed_dataset_map,
    recDict,
)
from . import api
from .. import db
from ..models import (
    BedFileMetadata,
    Intervals,
    Dataset,
    AverageIntervalData,
    IndividualIntervalData,
    AssociationIntervalData,
    Session,
    Collection,
)
from .authentication import auth
from .errors import forbidden, not_found, invalid


@api.route("/test", methods=["GET"])
def test():
    """test api calls"""
    return jsonify({"test": "Hello, world!"})


@api.route("/testProtected", methods=["GET"])
@auth.login_required
def test_protected():
    """test api calls"""
    return jsonify({"test": "Hello, world!"})


@api.route("/resolutions/", methods=["GET"])
@auth.login_required
def get_resolutions():
    """Gets available combinations of windowsizes and binsizes
    from config file"""
    return jsonify(current_app.config["PREPROCESSING_MAP"])


@api.route("/datasets/", methods=["GET"])
@auth.login_required
def get_all_datasets():
    """Gets all available datasets for a given user."""
    all_available_datasets = Dataset.query.filter(
        (Dataset.user_id == g.current_user.id)
        | (Dataset.public)
        | (Dataset.id.in_(g.session_datasets))
    ).all()
    update_processing_state(all_available_datasets, db)
    return jsonify([dfile.to_json() for dfile in all_available_datasets])


@api.route("/datasets/<dtype>", methods=["GET"])
@auth.login_required
def get_datasets(dtype):
    """Gets all available datasets for a given user."""
    if dtype == "cooler":
        cooler_files = Dataset.query.filter(
            (Dataset.filetype == "cooler")
            & ((g.current_user.id == Dataset.user_id) | (Dataset.public))
        ).all()
        update_processing_state(cooler_files, db)
        return jsonify([cfile.to_json() for cfile in cooler_files])
    elif dtype == "bed":
        bed_files = Dataset.query.filter(
            (Dataset.filetype == "bedfile")
            & ((g.current_user.id == Dataset.user_id) | (Dataset.public))
        ).all()
        update_processing_state(bed_files, db)
        return jsonify([bfile.to_json() for bfile in bed_files])
    elif dtype == "bigwig":
        bed_files = Dataset.query.filter(
            (Dataset.filetype == "bigwig")
            & ((g.current_user.id == Dataset.user_id) | (Dataset.public))
        ).all()
        update_processing_state(bed_files, db)
        return jsonify([bfile.to_json() for bfile in bed_files])
    else:
        return not_found(f"option: '{dtype}' not understood")


@api.route("/datasets/<dataset_id>/name/", methods=["GET"])
@auth.login_required
def get_name_of_dataset(dataset_id):
    """Returns the name for a given dataset, if the user owns the requested dataset."""
    dataset = Dataset.query.get(dataset_id)
    # check whether dataset exists
    if dataset is None:
        return not_found(f"Dataset with id '{dataset_id}' does not exist!")
    # check whether user owns the dataset
    if is_access_to_dataset_denied(dataset, g):
        return forbidden(
            f"Dataset with id '{dataset_id}' is not owned by logged in user!"
        )
    return jsonify(dataset.dataset_name)


@api.route("/datasets/<dataset_id>/processedDataMap/", methods=["GET"])
@auth.login_required
def get_processed_data_mapping_of_dataset(dataset_id):
    """Gets processed data map of a given region dataset.
    This object has the following structure:
    {
        processed_data_type: {
            associated_dataset_id: {
                name: NAME_OF_ASSOCIATED_DATASET,
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

    Processed_data_type is in [pileup, stackup, lineprofile]. All entries
    for a given processed_data_type key are available processed_datasets.
    The values for each processed_dataset hold information about their name
    and which id in the target table corresponds to which interval and binsize
    combintaion.
    """
    dataset = Dataset.query.get(dataset_id)
    # check whether dataset exists
    if dataset is None:
        return not_found(f"Dataset with id '{dataset_id}' does not exist!")
    # check whether user owns the dataset
    if is_access_to_dataset_denied(dataset, g):
        return forbidden(
            f"Dataset with id '{dataset_id}' is not owned by logged in user!"
        )
    # check whether dataset is bedfile
    if dataset.filetype != "bedfile":
        return invalid(f"Dataset with id '{dataset_id}' is not a bedfile!")
    # create output object
    output = {"pileup": recDict(), "stackup": recDict(), "lineprofile": recDict()}
    # populate output object
    associated_intervals = dataset.intervals.all()
    for interval in associated_intervals:
        average_data = interval.averageIntervalData.all()
        individual_data = interval.individualIntervalData.all()
        # add data
        add_average_data_to_preprocessed_dataset_map(average_data, output, g)
        add_individual_data_to_preprocessed_dataset_map(individual_data, output, g)
    return jsonify(output)


@api.route("/intervals/", methods=["GET"])
@auth.login_required
def get_intervals():
    """Gets all available intervals for a given user."""
    # SQL join to get all intervals that come from a dataset owned by the respective user
    all_files = (
        Intervals.query.join(Dataset)
        .filter(
            (Dataset.user_id == g.current_user.id)
            | (Dataset.public)
            | (Dataset.id.in_(g.session_datasets))
        )
        .all()
    )
    return jsonify([dfile.to_json() for dfile in all_files])


@api.route("/intervals/<interval_id>/metadata", methods=["GET"])
@auth.login_required
def get_interval_metadata(interval_id):
    """returns available metadata for given intervals."""
    interval = Intervals.query.get(interval_id)
    if interval is None:
        return not_found(f"Intervals with id {interval_id} do not exist!")
    # check if associated dataset is owned
    if is_access_to_dataset_denied(interval.source_dataset, g):
        return forbidden(
            f"Dataset associated with interval id {interval.id} is not owned by logged in user!"
        )
    # get associated metadata entries sorted by id in desecnding order; id sorting is necessary for newer metadata to win in field names
    metadata_entries = interval.source_dataset.bedFileMetadata.order_by(
        BedFileMetadata.id.desc()
    ).all()
    # check if list is empty
    if len(metadata_entries) == 0:
        return jsonify({})
    # get bed_row_index rom interval file -> this is the last column
    bed_row_index = pd.read_csv(interval.file_path, sep="\t", header=None).iloc[:, -1]
    # load all metadata_files as dataframes
    temp_frames = []
    for metadata_entry in metadata_entries:
        if metadata_entry.metadata_fields is None:
            # skip metadata if there are no fields defined
            continue
        columns_retained = json.loads(metadata_entry.metadata_fields)
        temp_frame = pd.read_csv(
            metadata_entry.file_path, usecols=columns_retained
        ).iloc[bed_row_index, :]
        temp_frames.append(temp_frame)
    output_frame = pd.concat(temp_frames, axis=1)
    # this drops all occurences of a given column but the first, since ids are sorted by descending order, the newest one wins
    output_frame_unique = output_frame.loc[:, ~output_frame.columns.duplicated()]
    return jsonify(output_frame_unique.to_dict(orient="list"))


@api.route("/averageIntervalData/<entry_id>/", methods=["GET"])
@auth.login_required
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
    if is_access_to_dataset_denied(cooler_ds, g) or is_access_to_dataset_denied(
        bed_ds, g
    ):
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
    if is_access_to_collection_denied(collection, g) or is_access_to_dataset_denied(
        bed_ds, g
    ):
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


@api.route("/individualIntervalData/<entry_id>/", methods=["GET"])
@auth.login_required
def get_stackup_data(entry_id):
    """returns stackup data for the specified stackup id if it exists and
    access is allowed."""
    # Check for existence
    if IndividualIntervalData.query.get(entry_id) is None:
        return not_found("Stackup does not exist!")
    stackup = IndividualIntervalData.query.get(entry_id)
    bigwig_ds = stackup.source_dataset
    bed_ds = stackup.source_intervals.source_dataset
    if is_access_to_dataset_denied(bigwig_ds, g) or is_access_to_dataset_denied(
        bed_ds, g
    ):
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
    if is_access_to_dataset_denied(bigwig_ds, g) or is_access_to_dataset_denied(
        bed_ds, g
    ):
        return forbidden(
            "Bigwig dataset or bed dataset is not owned by logged in user!"
        )
    # get associated metadata entries sorted by id; id sorting is necessary for newer metadata to win in field names
    metadata_entries = bed_ds.bedFileMetadata.order_by(BedFileMetadata.id.desc()).all()
    # check if list is empty or all metadata entries have undefiend metadata fields
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
    # this drops all occurences of a given column but the first, since ids are sorted by descending order, the newest one wins
    output_frame_unique = output_frame_large.loc[
        :, ~output_frame_large.columns.duplicated()
    ]
    # subset by stackup index
    stackup_index = np.load(down_sample_index)
    outframe = output_frame_unique.iloc[stackup_index, :]
    return jsonify(outframe.to_dict(orient="list"))


@api.route("/sessions/", methods=["GET"])
@auth.login_required
def get_all_sessions():
    """Gets all available sessions for a given user."""
    all_available_sessions = Session.query.filter(
        (Session.user_id == g.current_user.id)
    ).all()
    return jsonify([dfile.to_json() for dfile in all_available_sessions])


@api.route("/sessions/<session_id>/", methods=["GET"])
@auth.login_required
def get_session_data_with_id(session_id):
    """Returns session data with given id"""
    # check whether session with id exists
    session = Session.query.get(session_id)
    # check whether dataset exists
    if session is None:
        return not_found(f"Session with id '{session_id}' does not exist!")
    # check if session is owned
    if (session.user_id != g.current_user.id) and (session.id != g.session_id):
        return forbidden(f"Session with id '{session_id}' is not owned!")
    return jsonify(session.to_json())


@api.route("/sessions/<session_id>/sessionToken/", methods=["GET"])
@auth.login_required
def get_session_token(session_id):
    """Returns session token for a given session."""
    # check whether session with id exists
    session = Session.query.get(session_id)
    # check whether dataset exists
    if session is None:
        return not_found(f"Session with id '{session_id}' does not exist!")
    # check if session is owned
    if session.user_id != g.current_user.id:
        return forbidden(f"Session with id '{session_id}' is not owned!")
    # create session token
    return jsonify(
        {
            "session_token": session.generate_session_token(),
            "session_id": session_id,
        }
    )


@api.route("/collections/", methods=["GET"])
@auth.login_required
def get_all_collections():
    """Gets all available collections for a given user."""
    all_available_collections = Collection.query.filter(
        (Collection.user_id == g.current_user.id)
        | Collection.public
        | (Collection.id.in_(g.session_collections))
    ).all()
    return jsonify([dfile.to_json() for dfile in all_available_collections])
