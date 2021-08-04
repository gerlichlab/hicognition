"""Start hicognition server."""
import os
from getpass import getpass
import click
from base64 import b64encode
from app import create_app, db
from app.models import (
    User,
    Dataset,
    Intervals,
    Task,
    AverageIntervalData,
    BedFileMetadata,
    Session,
    Collection
)
from flask_migrate import Migrate
from flask.cli import AppGroup

app = create_app(os.getenv("FLASK_CONFIG") or "default")
migrate = Migrate(app, db, compare_type=True)

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
        user = User(username=name)
    # prompt for password if not defined
    if password is None:
        password = getpass(f"Enter password for {name}: ")
    user.set_password(password)
    db.session.add(user)
    db.session.commit()


app.cli.add_command(user_group)

# add command line arguments for dataset addition/preprocessing

dataset_group = AppGroup("dataset")


@dataset_group.command("add")
@click.argument("path")
@click.argument("name")
@click.argument("filetype")
@click.argument("user")
@click.argument("password")
@click.option("--description", "-d", default=None)
@click.option("--genotype", "-g", default=None)
@click.option("--public", "-p", default=False)
def add_dataset(path, name, filetype, user, password, description, genotype, public):
    """Adds dataset to database and uploads it."""
    client = app.test_client()
    headers = _get_api_headers(user, password)
    # construct form data
    with open(path, "rb") as f:
        data = {
            "datasetName": name,
            "description": description,
            "genotype": genotype,
            "filetype": filetype,
            "file": (f, path),
            "public": public,
        }
        # dispatch post request
        response = client.post(
            "/api/datasets/",
            data=data,
            headers=headers,
            content_type="multipart/form-data",
        )
    print(
        f"Request dispatched with status code {response.status_code} and response {response.json}"
    )


@dataset_group.command("preprocess")
@click.argument("name")
@click.argument("user")
@click.argument("password")
def add_dataset(name, user, password):
    """Triggers preprocessing for all datasets with name with all available regions."""
    client = app.test_client()
    headers = _get_api_headers(user, password)
    # get dataset with name
    datasets = Dataset.query.filter(Dataset.dataset_name == name).all()
    # check wheter dataset name is unique
    if len(datasets) > 1:
        raise ValueError("Name refers to multiple datasets!")
    dataset = datasets[0]
    if dataset.filetype not in ["cooler", "bigwig"]:
        raise ValueError("Source dataset is not a genomic feature dataset!")
    # get ids of all bedfiles
    bedfiles = Dataset.query.filter(Dataset.filetype == "bedfile").all()
    if len(bedfiles) == 0:
        raise ValueError("No bedfiles available!")
    # start preprocessing
    data = {
        "dataset_id": str(dataset.id),
        "region_ids": str([bedfile.id for bedfile in bedfiles]),
    }
    # dispatch post request
    response = client.post(
        "/api/preprocess/",
        data=data,
        headers=headers,
        content_type="multipart/form-data",
    )
    print(
        f"Request dispatched with status code {response.status_code} and response {response.json}"
    )


app.cli.add_command(dataset_group)


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
        "Collection": Collection
    }


# Helpers


def _get_api_headers(username, password):
    return {
        "Authorization": "Basic "
        + b64encode((username + ":" + password).encode("utf-8")).decode("utf-8"),
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
