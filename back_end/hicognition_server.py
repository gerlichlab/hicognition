"""Start hicognition server."""
import os
import atexit
import logging

# import json
from getpass import getpass
from base64 import b64encode
import click
from app import create_app, db
from app.background_tasks import (
    cleanup_empty_tasks,
    cleanup_failed_tasks,
    add_app_context,
    send_keep_alive_message,
)
from app.models import *

# (
#     User,
#     Dataset,
#     Intervals,
#     Task,
#     AverageIntervalData,
#     BedFileMetadata,
#     Session,
#     Collection,
#     EmbeddingIntervalData,
#     AssociationIntervalData,
#     Organism,
#     Assembly,
# )
from flask_migrate import Migrate
from flask.cli import AppGroup
from apscheduler.schedulers.background import BackgroundScheduler

app = create_app(os.getenv("FLASK_CONFIG") or "default")
migrate = Migrate(app, db, compare_type=True)

# start background tasks
if not app.config["SHOWCASE"]:
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(add_app_context(app)(cleanup_empty_tasks), "interval", seconds=360)
    sched.add_job(add_app_context(app)(cleanup_failed_tasks), "interval", seconds=520)
    sched.add_job(add_app_context(app)(send_keep_alive_message), "interval", seconds=30)
    sched.start()
    atexit.register(lambda: sched.shutdown(wait=False))

# add command line arguments for user creation

user_group = AppGroup("user")


@user_group.command("define")
@click.argument("name")
@click.option("--password", "-p", default=None)
def create_user(name, password):
    """Creates a new user either with defined password or password prompt.
    If user with the name exists already, password is redefined."""
    # check if user with such a name exists
    if User.query.filter(User.username == name).first() is not None:
        # if user exists, get the user
        user = User.query.filter(User.username == name).first()
    else:
        # otherwise make a new one
        # and confirm email, email address stays empty form manual created users
        user = User(username=name, email_confirmed = True)
    # prompt for password if not defined
    if password is None:
        password = getpass(f"Enter password for {name}: ")
    user.set_password(password)
    db.session.add(user)
    db.session.commit()


app.cli.add_command(user_group)

# # add command line arguments for dataset addition/preprocessing

# dataset_group = AppGroup("dataset")


# @dataset_group.command("add")
# @click.argument("json_path")
# @click.argument("user")
# @click.argument("password")
# def add_dataset(json_path, user, password):
#     """Adds datasets defined in a JSON to database and uploads it."""
#     client = app.test_client()
#     headers = _get_api_headers(user, password)
#     # construct form data from JSON
#     with open(json_path, "rb") as json_data:
#         all_data = json.load(json_data)
#         for dataset_item in all_data["dataset"]:
#             # print(dataset_item)
#             with open(dataset_item["file"], "rb") as file:
#                 # open and pass the file into the data array as well
#                 dataset_item["file"] = (file, dataset_item["file"])
#                 response = client.post(
#                     "/api/datasets/",
#                     data=dataset_item,
#                     headers=headers,
#                     content_type="multipart/form-data",
#                 )
#                 print(
#                     f"Request dispatched with status code {response.status_code} and response {response.json}"
#                 )


# @dataset_group.command("preprocess")
# @click.argument("name")
# @click.argument("user")
# @click.argument("password")
# def add_dataset(name, user, password):
#     """Triggers preprocessing for all datasets with name with all available regions."""
#     client = app.test_client()
#     headers = _get_api_headers(user, password)
#     # get dataset with name
#     datasets = Dataset.query.filter(Dataset.dataset_name == name).all()
#     # check if dataset name is unique
#     if len(datasets) > 1:
#         raise ValueError("Name refers to multiple datasets!")
#     dataset = datasets[0]
#     if dataset.filetype not in ["cooler", "bigwig"]:
#         raise ValueError("Source dataset is not a genomic feature dataset!")
#     # get ids of all bedfiles
#     bedfiles = Dataset.query.filter(Dataset.filetype == "bedfile").all()
#     if len(bedfiles) == 0:
#         raise ValueError("No bedfiles available!")
#     # start preprocessing
#     data = {
#         "dataset_id": str(dataset.id),
#         "region_ids": str([bedfile.id for bedfile in bedfiles]),
#     }
#     # dispatch post request
#     response = client.post(
#         "/api/preprocess/",
#         data=data,
#         headers=headers,
#         content_type="multipart/form-data",
#     )
#     print(
#         f"Request dispatched with status code {response.status_code} and response {response.json}"
#     )


# app.cli.add_command(dataset_group)


@app.shell_context_processor
def make_shell_context():
    """Make shell context for app."""
    return {
        "db": db,
        "User": User,
        "Dataset": Dataset,
        "Intervals": Intervals,
        "Task": Task,
        "AverageIntervalData": AverageIntervalData,
        "BedFileMetadata": BedFileMetadata,
        "Session": Session,
        "Collection": Collection,
        "EmbeddingIntervalData": EmbeddingIntervalData,
        "AssociationIntervalData": AssociationIntervalData,
        "Organism": Organism,
        "Assembly": Assembly,
        "Repository": Repository,
        "RepositoryAuth": RepositoryAuth,
    }


# helpers


def _get_api_headers(username, password):
    return {
        "Authorization": "Basic "
        + b64encode((username + ":" + password).encode("utf-8")).decode("utf-8"),
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


# make script entrypoint


if __name__ == "__main__":
    app.run()
