"""Helpers to populate database"""
import json
from pathlib import Path
from flask.globals import current_app
import pandas as pd
from ..models import (
    Repository,
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
    if db.session.query(Repository).first() is None:
        for repo_dict in current_app.config["REPOSITORIES"]:
            repo = Repository(
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
    if current_app.config["END2END"]:
        create_test_user("test", "test")
