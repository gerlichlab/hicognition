"""Start hicognition server."""
import os
from getpass import getpass
import click
from app import create_app, db
from app.models import (
    User,
    Dataset,
    Intervals,
    Task,
    AverageIntervalData,
    BedFileMetadata,
)
from flask_migrate import Migrate
from flask.cli import AppGroup

app = create_app(os.getenv("FLASK_CONFIG") or "default")
migrate = Migrate(app, db)

# add command line arguments for user creation

user_group = AppGroup("user")
@user_group.command('define')
@click.argument('name')
@click.option('--password','-p', default=None)
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
    }
