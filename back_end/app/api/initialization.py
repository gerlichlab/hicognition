"""Helpers to populate database"""
import json
from pathlib import Path
from flask.globals import current_app
import pandas as pd
from ..models import (
    DataRepository,
    User,
    Organism,
    Assembly,
    Dataset,
    dataset_preprocessing_table,
    collections_preprocessing_table,
    Task,
)
from . import api
from .. import db


def add_path(value, path):
    if pd.isnull(value):
        return pd.NA
    else:
        return Path(path) / Path(value).name


def change_file_paths_to_showcase(df, showcase_dir="/showcase_data/raw_data"):
    """Changes file paths to use showcase directory"""
    output = df.copy()
    if "file_path" in df.columns:
        output.loc[:, "file_path"] = df.file_path.apply(
            lambda x: add_path(x, showcase_dir)
        )
    if "file_path_feature_values" in df.columns:
        output.loc[:, "file_path_feature_values"] = df.file_path_feature_values.apply(
            lambda x: add_path(x, showcase_dir)
        )
    if "cluster_id_path" in df.columns:
        output.loc[:, "cluster_id_path"] = df.cluster_id_path.apply(
            lambda x: add_path(x, showcase_dir)
        )
    if "thumbnail_path" in df.columns:
        output.loc[:, "thumbnail_path"] = df.thumbnail_path.apply(
            lambda x: add_path(x, showcase_dir)
        )
    if "file_path_small" in df.columns:
        output.loc[:, "file_path_small"] = df.file_path_small.apply(
            lambda x: add_path(x, showcase_dir)
        )
    return output


def add_showcase_data():
    """Adds showcase data"""
    # load tables
    datasets = pd.read_csv("/showcase_data/database_state/datasets.csv")
    datasets.loc[:, "user_id"] = pd.NA
    intervals = pd.read_csv("/showcase_data/database_state/intervals.csv")
    intervals.loc[:, "file_path_sub_sample_index"] = pd.NA
    collections = pd.read_csv("/showcase_data/database_state/collections.csv")
    collections.loc[:, "user_id"] = pd.NA
    collection_assoc_table = pd.read_csv(
        "/showcase_data/database_state/dataset_collection_association_table.csv"
    )[["collection_id", "dataset_id"]]
    sessions = pd.read_csv("/showcase_data/database_state/sessions.csv")
    sessions.loc[:, "user_id"] = pd.NA
    # load session data
    with open("/showcase_data/database_state/session_data.json", "r") as f:
        text = f.read()
    session_objects = [str(i["session_object"]) for i in json.loads(text)]
    session_frame = sessions.assign(session_object=session_objects)
    session_coll = pd.read_csv(
        "/showcase_data/database_state/session_collection_association.csv"
    )
    session_data = pd.read_csv(
        "/showcase_data/database_state/session_dataset_association.csv"
    )
    avg = pd.read_csv("/showcase_data/database_state/average_interval_data.csv")
    emb = pd.read_csv("/showcase_data/database_state/embedding_interval_data.csv")
    ind = pd.read_csv("/showcase_data/database_state/individual_interval_data.csv")
    assoc = pd.read_csv("/showcase_data/database_state/association_interval_data.csv")
    # add data
    datasets.to_sql("dataset", db.get_engine(), if_exists="append", index=False)
    intervals.to_sql("intervals", db.get_engine(), if_exists="append", index=False)
    collections.to_sql("collection", db.get_engine(), if_exists="append", index=False)
    collection_assoc_table.to_sql(
        "dataset_collection_assoc_table",
        db.get_engine(),
        if_exists="append",
        index=False,
    )
    session_frame.to_sql("session", db.get_engine(), if_exists="append", index=False)
    session_coll.to_sql(
        "session_collection_assoc_table",
        db.get_engine(),
        if_exists="append",
        index=False,
    )
    session_data.to_sql(
        "session_dataset_assoc_table", db.get_engine(), if_exists="append", index=False
    )
    change_file_paths_to_showcase(avg).to_sql(
        "average_interval_data", db.get_engine(), if_exists="append", index=False
    )
    change_file_paths_to_showcase(emb).to_sql(
        "embedding_interval_data", db.get_engine(), if_exists="append", index=False
    )
    change_file_paths_to_showcase(ind).to_sql(
        "individual_interval_data", db.get_engine(), if_exists="append", index=False
    )
    change_file_paths_to_showcase(assoc).to_sql(
        "association_interval_data", db.get_engine(), if_exists="append", index=False
    )


def create_hg19():
    """Creates entry for standard hg19 assembly and
    associates it with all available datasets."""
    if Assembly.query.first() is None:
        org = Organism(name="Human")
        db.session.add(org)
        db.session.commit()
        assembly = Assembly(
            name="hg19",
            chrom_sizes=current_app.config["CHROM_SIZES"],
            chrom_arms=current_app.config["CHROM_ARMS"],
            organism_id=org.id,
        )
        db.session.add_all([org, assembly])
        db.session.commit()
        # add assembly id to all datasets
        for dataset in Dataset.query.all():
            dataset.assembly = assembly.id
        db.session.commit()


def add_repositories():
    """adds repositories depending on info in config file"""
    if db.session.query(DataRepository).first() is None:
        for repo_dict in current_app.config["REPOSITORIES"]:
            repo = DataRepository(
                name=repo_dict["name"],
                url=repo_dict["url"],
                file_url=repo_dict["file_url"],
                auth_required=repo_dict["auth_required"],
            )
            db.session.add(repo)
        db.session.commit()


def drop_preprocessing_tables():
    """Deletes entries in preprocessing tables."""
    stmt = dataset_preprocessing_table.delete()
    db.session.execute(stmt)
    stmt = collections_preprocessing_table.delete()
    db.session.execute(stmt)
    db.session.commit()


def drop_tasks():
    """Deletes entries in tasks table."""
    tasks = Task.query.all()
    for task in tasks:
        db.session.delete(task)
    db.session.commit()


def create_test_user(name, password):
    """Creates a test user or gets the user if it exists."""
    # check if user with such a name exists
    if User.query.filter(User.username == name).first() is not None:
        # if user exists, get the user
        user = User.query.filter(User.username == name).first()
    else:
        # otherwise make a new one
        user = User(username=name)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()


@api.before_app_first_request
def init_database():
    """Populate database"""
    if not current_app.config["TESTING"]:
        create_hg19()
        drop_preprocessing_tables()
        drop_tasks()
        add_repositories()
    # add showcase data if needed
    if (
        current_app.config["SHOWCASE"]
        and (len(Dataset.query.all()) == 0)
        and (not current_app.config["TESTING"])
        and (not current_app.config["END2END"])
    ):
        add_showcase_data()
    if current_app.config["END2END"]:
        create_test_user("test", "test")
