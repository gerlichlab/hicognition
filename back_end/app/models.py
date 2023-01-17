"""Database models for HiCognition."""
# TODO refactor to allow database to not know about flask-server or similar
# TODO task launcher: why put it into the user class?

import os
from abc import abstractmethod
import datetime
from enum import Enum
import json
import pandas as pd
from flask.globals import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from sqlalchemy.ext.declarative import declared_attr
import rq
import redis
import cooler
from itertools import chain
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import JSONWebSignatureSerializer
from . import lib as hicognition
from .lib.utils import parse_binsizes
from .lib.format_checkers import FORMAT_CHECKERS
from . import db


# define association tables

session_dataset_assoc_table = db.Table(
    "session_dataset_assoc_table",
    db.Column(
        "session_id", db.Integer, db.ForeignKey("session.id", ondelete="CASCADE")
    ),
    db.Column(
        "dataset_id", db.Integer, db.ForeignKey("dataset.id", ondelete="CASCADE")
    ),
)

session_collection_assoc_table = db.Table(
    "session_collection_assoc_table",
    db.Column(
        "session_id", db.Integer, db.ForeignKey("session.id", ondelete="CASCADE")
    ),
    db.Column(
        "collection_id", db.Integer, db.ForeignKey("collection.id", ondelete="CASCADE")
    ),
)

dataset_collection_assoc_table = db.Table(
    "dataset_collection_assoc_table",
    db.Column(
        "collection_id", db.Integer, db.ForeignKey("collection.id", ondelete="CASCADE")
    ),
    db.Column(
        "dataset_id", db.Integer, db.ForeignKey("dataset.id", ondelete="CASCADE")
    ),
)

dataset_preprocessing_table = db.Table(
    "dataset_dataset_preprocessing_table",
    db.Column(
        "dataset_region", db.Integer, db.ForeignKey("dataset.id", ondelete="CASCADE")
    ),
    db.Column(
        "dataset_feature", db.Integer, db.ForeignKey("dataset.id", ondelete="CASCADE")
    ),
    db.UniqueConstraint("dataset_region", "dataset_feature", name="uix_1"),
)

dataset_failed_table = db.Table(
    "dataset_failed_table",
    db.Column(
        "dataset_region", db.Integer, db.ForeignKey("dataset.id", ondelete="CASCADE")
    ),
    db.Column(
        "dataset_feature", db.Integer, db.ForeignKey("dataset.id", ondelete="CASCADE")
    ),
    db.UniqueConstraint("dataset_region", "dataset_feature", name="uix_1"),
)

dataset_completed_table = db.Table(
    "dataset_completed_table",
    db.Column(
        "dataset_region", db.Integer, db.ForeignKey("dataset.id", ondelete="CASCADE")
    ),
    db.Column(
        "dataset_feature", db.Integer, db.ForeignKey("dataset.id", ondelete="CASCADE")
    ),
    db.UniqueConstraint("dataset_region", "dataset_feature", name="uix_1"),
)

collections_preprocessing_table = db.Table(
    "collections_preprocessing_table",
    db.Column(
        "dataset_region", db.Integer, db.ForeignKey("dataset.id", ondelete="CASCADE")
    ),
    db.Column(
        "collection_feature",
        db.Integer,
        db.ForeignKey("collection.id", ondelete="CASCADE"),
    ),
    db.UniqueConstraint("dataset_region", "collection_feature", name="uix_1"),
)

collections_failed_table = db.Table(
    "collections_failed_table",
    db.Column(
        "dataset_region", db.Integer, db.ForeignKey("dataset.id", ondelete="CASCADE")
    ),
    db.Column(
        "collection_feature",
        db.Integer,
        db.ForeignKey("collection.id", ondelete="CASCADE"),
    ),
    db.UniqueConstraint("dataset_region", "collection_feature", name="uix_1"),
)


class User(db.Model, UserMixin):
    """User database model"""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    email_confirmed = db.Column(db.Boolean, default=False)
    created_at = db.Column(
        db.DateTime,  default=datetime.datetime.utcnow
    )
    datasets = db.relationship(
        "Dataset", backref="owner", lazy="dynamic", cascade="all, delete-orphan"
    )
    tasks = db.relationship(
        "Task", backref="user", lazy="dynamic", cascade="all, delete-orphan"
    )
    credentials = db.relationship(
        "RepositoryAuth",
        backref="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    # def add_repository_credentials(
    #     self, repository_name: str, key: str, secret: str
    # ):  # TODO needed?
    #     credentials = RepositoryAuth(self.id, repository_name, key, secret)
    #     db.session.add(credentials)
    #     return credentials

    def set_password(self, password):
        """set password helper."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """check password helper."""
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expiration):
        """generates authentication token"""
        serializer = Serializer(current_app.config["SECRET_KEY"], expires_in=expiration)
        return serializer.dumps({"id": self.id}).decode("utf-8")

    # TODO continue working on this
    # TODO move to Task class, have started on this already but commented out
    def launch_task(self, queue, func, description, dataset_id=None, collection_id=None, *args, **kwargs):
        """adds task to queue"""
        if dataset_id:
            args = [dataset_id, *args]
        if collection_id:
            args = [collection_id, *args]

        # check if func is name of function in tasks.py, then import those
        if isinstance(func, str):
            import app.tasks
            func = app.tasks.__getattr__(func)

        rq_job = queue.enqueue(
            _rq_job_wrapper, func, *args, **kwargs, job_timeout="10h"
        )

        task = Task(
            id=rq_job.get_id(),
            name=func,
            description=description,
            user_id=self.id,
            dataset_id=dataset_id,
            collection_id=collection_id,
            intervals_id=kwargs.get("intervals_id", None),
        )
        db.session.add(task)
        return task

    def get_tasks_in_progress(self):
        """gets all uncompleted tasks"""
        return Task.query.filter_by(user=self, complete=False).all()

    def get_task_in_progress(self, name):
        """gets a particular uncompleted task"""
        return Task.query.filter_by(name=name, user=self, complete=False).first()

    @staticmethod
    def verify_auth_token(token):
        """verify the user token"""
        serializer = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = serializer.loads(token)
        except:
            return None
        return User.query.get(data["id"])

    def __repr__(self):
        """Format print output."""
        return f"<User {self.username}>"


class Repository(db.Model):
    """Model for external data repositories.
    Name is primary key, as this table will hold only a few rows and it makes
    handling gets/posts easier.

    url must contain an {href} tag.
    file_url must contain the {id} tag.
    """

    # fields
    name = db.Column(db.String(64), nullable=False, primary_key=True)
    url = db.Column(db.String(512), default="")
    file_url = db.Column(db.String(512), default="")
    auth_required = db.Column(db.Boolean, default=False)

    def build_url_sample(self, data_id: str):
        """inserts id into repo metadata url"""
        return self.file_url.format(id=data_id)

    def build_url(self, href: str):
        """inserts href into general repo url"""
        return self.url.format(href=href)

    credentials = db.relationship(
        "RepositoryAuth",
        back_populates="repository",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def to_json(self):
        """makes dict from model object"""
        d = dict()
        for c in self.__table__.columns:
            d[c.name] = str(getattr(self, c.name))
        return d


class RepositoryAuth(db.Model):  # TODO change name
    """Optional many-to-many object to store user keys for external repos"""

    # fields
    user_id = db.Column(
        db.ForeignKey("user.id", name="fk_repoauth_user"), primary_key=True
    )
    repository_name = db.Column(
        db.ForeignKey("repository.name", name="fk_repoauth_repo"), primary_key=True
    )
    key = db.Column(db.String(512), nullable=False)
    secret = db.Column(db.String(512), nullable=False)

    # assoc
    # user = db.relationship("User", back_populates='credentials')
    repository = db.relationship("Repository", back_populates="credentials")


class Dataset(db.Model):
    """Dataset database model"""

    # fields
    id = db.Column(db.Integer, primary_key=True)
    dataset_name = db.Column(db.String(512), nullable=False)
    description = db.Column(db.String(81), default="undefined")
    created_at = db.Column(
        db.DateTime,  default=datetime.datetime.utcnow
    )
    sizeType = db.Column(db.String(64), default="undefined")
    file_path = db.Column(db.String(512))
    public = db.Column(db.Boolean, default=False, nullable=False)
    filetype = db.Column(db.String(64), nullable=False)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", name="fk_dataset_user"), nullable=False
    )
    processing_state = db.Column(
        db.String(64)
    )  # 'new', 'processing', 'processing_failed', 'success'
    repository_name = db.Column(
        db.ForeignKey("repository.name", name="fk_dataset_repository"), nullable=True
    )
    sample_id = db.Column(db.String(128), nullable=True)
    source_url = db.Column(db.String(512), nullable=True)
    upload_state = db.Column(
        db.String(64), nullable=False, default="new"
    )  # Enum('new', 'uploading', 'uploaded', 'upload_failed')
    cell_type = db.Column(db.String(64), default="undefined")
    perturbation = db.Column(db.String(64), default="undefined")

    # self relationships
    processing_features = db.relationship(
        "Dataset",
        secondary=dataset_preprocessing_table,
        primaryjoin=dataset_preprocessing_table.c.dataset_region == id,
        secondaryjoin=dataset_preprocessing_table.c.dataset_feature == id,
        backref="processing_regions",
    )
    failed_features = db.relationship(
        "Dataset",
        secondary=dataset_failed_table,
        primaryjoin=dataset_failed_table.c.dataset_region == id,
        secondaryjoin=dataset_failed_table.c.dataset_feature == id,
        backref="failed_regions",
    )
    completed_features = db.relationship(
        "Dataset",
        secondary=dataset_completed_table,
        primaryjoin=dataset_completed_table.c.dataset_region == id,
        secondaryjoin=dataset_completed_table.c.dataset_feature == id,
        backref="completed_regions",
    )
    # relationship
    assembly = db.Column(
        db.Integer, db.ForeignKey("assembly.id", name="fk_dataset_assembly")
    )
    intervals = db.relationship(
        "Intervals",
        back_populates="source_dataset",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    obs_exp = db.relationship(
        "ObsExp",
        backref="computed_for",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    collections = db.relationship(
        "Collection", secondary=dataset_collection_assoc_table
    )
    processing_collections = db.relationship(
        "Collection", secondary=collections_preprocessing_table
    )
    failed_collections = db.relationship(
        "Collection", secondary=collections_failed_table
    )
    sessions = db.relationship("Session", secondary=session_dataset_assoc_table)
    averageIntervalData = db.relationship(
        "AverageIntervalData",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    individualIntervalData = db.relationship(
        "IndividualIntervalData",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    embeddingData = db.relationship(
        "EmbeddingIntervalData",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    bedFileMetadata = db.relationship(
        "BedFileMetadata",
        backref="associated_dataset",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    @property
    def interval_data(self):
        """makes a big list of interval data objects"""
        return [
            *self.averageIntervalData,
            *self.individualIntervalData,
            *self.embeddingData,
        ]

    tasks = db.relationship(
        "Task", backref="dataset", lazy="dynamic", cascade="all, delete-orphan"
    )
    repository = db.relationship("Repository")
    user = db.relationship("User")

    def get_tasks_in_progress(self):
        """Gets the tasks in progress for the dataset."""
        return Task.query.filter_by(dataset=self, complete=False).all()

    def __repr__(self):
        """Format print output."""
        return f"<Dataset {self.dataset_name}>"

    def set_processing_state(self, database):
        """sets the current processing state of the dataset instance.
        Launching task sets processing state, this sets finished/failed state"""
        if self.processing_state not in ["processing", "finished", "failed"]:
            return
        # check if there are any unfinished tasks
        tasks = self.tasks.filter(Task.complete.is_(False)).all()
        if len(tasks) == 0:
            self.processing_state = "finished"
        else:
            if all_tasks_finished(tasks):
                self.processing_state = "finished"
            elif any_tasks_failed(tasks):
                self.processing_state = "failed"
            else:
                self.processing_state = "processing"
        database.session.add(self)
        database.session.commit()

    # @property # uli
    # def processing_state(self):
    #     failed = sum([iv_data.job_status == 'failed' for iv_data in self.interval_data]) > 0
    #     success = sum([iv_data.job_status == 'success' for iv_data in self.interval_data]) > 0
    #     running_tasks = [iv_data for iv_data in self.interval_data if iv_data.job_status not in ['failed', 'success']]

    #     if failed:
    #         return "failed"
    #     elif success:
    #         return "success"
    #     else:
    #         return "processing"

    def is_access_denied(self, app_context):
        """Determine whether context
        allows access to dataset."""
        if current_app.config["SHOWCASE"]:
            return False
        if self.public:
            return False
        if (self.user_id != app_context.current_user.id) and (
            self.id not in app_context.session_datasets
        ):
            return True
        return False

    def copy(self, **kwargs):
        dataset = Dataset()
        for column in self.__class__.__table__.c.keys():
            # forbid id, dataset_name and public flag
            if column in ["id", "dataset_name", "public"]:
                continue
            setattr(dataset, column, getattr(self, column))

        for key, value in kwargs.items():
            if key in self.__class__.__table__.c.keys():
                setattr(dataset, key, value)

        return dataset

    def delete_data_of_associated_entries(self):
        """deletes files of associated entries"""
        # join lists
        deletion_queue = chain(
            [self],
            *[x.interval_data for x in self.intervals.all()],
            self.intervals.all(),
            self.bedFileMetadata.all(),
            self.individualIntervalData.all(),
            self.embeddingData.all(),
            self.averageIntervalData.all(),
        )
        # create set form joined list
        for entry in set(deletion_queue):
            if isinstance(entry, IndividualIntervalData):
                hicognition.io_helpers.remove_safely(
                    entry.file_path_small, current_app.logger
                )
            if hasattr(entry, "file_path") and (entry.file_path is not None):
                hicognition.io_helpers.remove_safely(
                    entry.file_path, current_app.logger
                )
            if hasattr(entry, "file_path_sub_sample_index") and (
                entry.file_path_sub_sample_index is not None
            ):
                hicognition.io_helpers.remove_safely(
                    entry.file_path_sub_sample_index, current_app.logger
                )

    def remove_failed_tasks_for_region(self, database, region):
        """Remove failed tasks for self with region"""
        associated_tasks = (
            Task.query.join(Intervals)
            .join(Dataset)
            .filter(
                (Dataset.id == region.id)
                & (Task.dataset_id == self.id)
                & (Task.complete.is_(False))
            )
            .all()
        )
        failed_tasks = Task.filter_failed_tasks(associated_tasks)
        for task in failed_tasks:
            database.session.delete(task)
        database.session.commit()

    def get_missing_windowsizes(self, preprocessing_map):
        """Creates intervals that are in preprocessing_map, but
        do not exist for dataset"""
        if self.sizeType == "Interval":
            return []
        windowsizes = [
            windowsize
            for windowsize in preprocessing_map.keys()
            if windowsize != "variable"
        ]
        existing_windowsizes = set(
            [intervals.windowsize for intervals in self.intervals]
        )
        missing_windowsizes = []
        for target_windowsize in windowsizes:
            if target_windowsize not in existing_windowsizes:
                missing_windowsizes.append(target_windowsize)
        return missing_windowsizes

    def validate_dataset(self, delete=False):  # FIXME -> delete should be outside
        """Validates a dataset's file: checks whether file is in the right format.
        Deletes the dataset if invalid and delete is true.

        Args:
            delete (bool, optional): If invalid deletes file + dataset. Defaults to False.

        Returns:
            bool: file validity
        """
        assembly = Assembly.query.get(self.assembly)
        chromosome_names = set(
            pd.read_csv(assembly.chrom_sizes, header=None, sep="\t")[0]
        )
        needed_resolutions = parse_binsizes(
            current_app.config["PREPROCESSING_MAP"], "cooler"
        )
        valid = FORMAT_CHECKERS[self.filetype](
            self.file_path, chromosome_names, needed_resolutions
        )

        if not valid and delete:
            db.session.delete(self)
            db.session.commit()
            os.remove(self.file_path)

        return valid

    def preprocess_dataset(self):
        """Invokes preprocessing of dataset."""

        # start preprocessing of bedfile, the other filetypes do not need preprocessing
        if self.filetype in ["bedfile"]:#, "bedpe_file"]:
            import app.tasks

            self.user.launch_task(  #  TODO current user or dataset owner user?
                current_app.queues["short"],
                app.tasks.pipeline_bed,
                "run bed preprocessing",
                self.id,
            )
            self.processing_state = "processing"

        # if filetype is cooler, store available binsizes
        if self.filetype == "cooler":
            binsizes = [
                resolution.split("/")[2]
                for resolution in cooler.fileops.list_coolers(self.file_path)
            ]
            self.available_binsizes = json.dumps(binsizes)

        db.session.commit()

    def to_json(self):
        """Generates a JSON from the model"""
        json_dataset = {}
        for column in self.__class__.__table__.c.keys():
            if column not in ['created_at']:
                json_dataset[column] = getattr(self, column)

        # add processing datasets
        json_dataset["processing_datasets"] = [
            dataset.id for dataset in self.processing_features
        ]
        # add failed datasets
        json_dataset["failed_datasets"] = [
            dataset.id for dataset in self.failed_features
        ]
        # add processing collections
        json_dataset["processing_collections"] = [
            collection.id for collection in self.processing_collections
        ]
        # add failed collections
        json_dataset["failed_collections"] = [
            collection.id for collection in self.failed_collections
        ]
        return json_dataset


class Collection(db.Model):
    """Collections of datasets with optional name and description.
    One dataset can belong to many collections and one collection can
    have many datasets."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1024))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_at = db.Column(
        db.DateTime,  default=datetime.datetime.utcnow
    )
    public = db.Column(db.Boolean, default=False)
    kind = db.Column(
        db.String(256)
    )  # What kind of datasets are collected (regions, 1d-features, 2d-features)
    tasks = db.relationship("Task", backref="collection", lazy="dynamic")
    datasets = db.relationship("Dataset", secondary=dataset_collection_assoc_table)
    processing_for_datasets = db.relationship(
        "Dataset", secondary=collections_preprocessing_table
    )
    failed_for_datasets = db.relationship("Dataset", secondary=collections_failed_table)
    sessions = db.relationship("Session", secondary=session_collection_assoc_table)

    associationData = db.relationship(
        "AssociationIntervalData",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    embeddingData = db.relationship(
        "EmbeddingIntervalData",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    processing_state = db.Column(db.String(64))

    def get_tasks_in_progress(self):
        """Gets the Task that are in progress for the collection"""
        return Task.query.filter_by(collection=self, complete=False).all()

    def is_access_denied(self, app_context):
        """Determine whether context
        allows access to collection."""
        if current_app.config["SHOWCASE"]:
            return False
        if self.public:
            return False
        if (self.user_id != app_context.current_user.id) and (
            self.id not in app_context.session_collections
        ):
            return True
        return False

    def is_deletion_denied(self, app_context):
        """Determines whether context
        allows dataset deletion"""
        return self.user_id != app_context.current_user.id

    def delete_data_of_associated_entries(self):
        """Deletes associated Data"""
        assoc_data = self.associationData  # .all()
        deletion_queue = assoc_data
        for entry in deletion_queue:
            # remove files
            hicognition.io_helpers.remove_safely(entry.file_path, current_app.logger)
            if hasattr(entry, "file_path_feature_values"):
                hicognition.io_helpers.remove_safely(
                    entry.file_path_feature_values, current_app.logger
                )

    def set_processing_state(self, database):
        """Sets the current processing state of the collection instance.
        Launching task sets processing state, this sets finished/failed state"""
        if self.processing_state not in ["processing", "finished", "failed"]:
            return
        # check if there are any unfinished tasks
        tasks = self.tasks.filter(Task.complete.is_(False)).all()
        if len(tasks) == 0:
            self.processing_state = "finished"
        else:
            if all_tasks_finished(tasks):
                self.processing_state = "finished"
            elif any_tasks_failed(tasks):
                self.processing_state = "failed"
            else:
                self.processing_state = "processing"
        database.session.add(self)
        database.session.commit()

    def remove_failed_tasks_for_region(self, database, region):
        """Remove failed tasks for self with region"""
        associated_tasks = (
            Task.query.join(Intervals)
            .join(Dataset)
            .filter(
                (Dataset.id == region.id)
                & (Task.collection_id == self.id)
                & (Task.complete.is_(False))
            )
            .all()
        )
        failed_tasks = Task.filter_failed_tasks(associated_tasks)
        for task in failed_tasks:
            database.session.delete(task)
        database.session.commit()

    def to_json(self):
        """Formats json output."""
        json_session = {
            "id": self.id,
            "name": self.name,
            "kind": self.kind,
            "assembly": self.datasets[0].assembly,
            "number_datasets": len(self.datasets),
            "dataset_names": [dataset.dataset_name for dataset in self.datasets],
            "dataset_ids": [dataset.id for dataset in self.datasets],
            "processing_state": self.processing_state,
            "processing_for_regions": [
                region.id for region in self.processing_for_datasets
            ],
        }
        return json_session

    def __repr__(self):
        """Format print output."""
        return f"<Collection {self.name}>"


class ObsExp(db.Model):
    """Cache table for obs/exp dataframes"""

    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey("dataset.id"))
    binsize = db.Column(db.Integer, index=True)
    filepath = db.Column(db.String(512), index=True)


class Organism(db.Model):
    """Organism table for genome assembly"""

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(
        db.DateTime,  default=datetime.datetime.utcnow
    )
    name = db.Column(db.String(512))
    assemblies = db.relationship(
        "Assembly",
        backref="source_organism",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def to_json(self):
        """Generates json output."""
        return {"id": self.id, "name": self.name}


class Assembly(db.Model):
    """Genome assembly database model"""

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(
        db.DateTime,  default=datetime.datetime.utcnow
    )
    name = db.Column(db.String(512))
    chrom_sizes = db.Column(db.String(512), index=True)
    chrom_arms = db.Column(db.String(512), index=True)
    organism_id = db.Column(db.Integer, db.ForeignKey("organism.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def to_json(self):
        """Generates json output."""
        json_dataset = {"id": self.id, "name": self.name, "user_id": self.user_id}
        return json_dataset


class Intervals(db.Model):
    """Genomic IntervalData database model"""

    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey("dataset.id", ondelete="CASCADE"))
    created_at = db.Column(
        db.DateTime,  default=datetime.datetime.utcnow
    )
    name = db.Column(db.String(512), index=True)
    file_path_sub_sample_index = db.Column(db.String(512), index=True)
    windowsize = db.Column(db.Integer, index=True)

    source_dataset = db.relationship("Dataset", back_populates="intervals")
    tasks = db.relationship(
        "Task", backref="intervals", lazy="dynamic", cascade="all, delete-orphan"
    )

    @classmethod
    def __declare_last__(cls):
        # cls.interval_data = db.relationship("BaseIntervalData", backref="interval",)
        cls.average_interval_data = db.relationship(
            "AverageIntervalData", cascade="all, delete-orphan"
        )
        cls.individual_interval_data = db.relationship(
            "IndividualIntervalData", cascade="all, delete-orphan"
        )
        cls.association_interval_data = db.relationship(
            "AssociationIntervalData", cascade="all, delete-orphan"
        )
        cls.embedding_interval_data = db.relationship(
            "EmbeddingIntervalData", cascade="all, delete-orphan"
        )

    @property
    def interval_data(self):
        return [
            *self.average_interval_data,
            *self.individual_interval_data,
            *self.association_interval_data,
            *self.embedding_interval_data,
        ]

    def __repr__(self):
        """Format print output."""
        return f"<Intervals {self.name}>"

    def to_json(self):
        """Formats json output."""
        json_intervals = {
            "id": self.id,
            "source_dataset": self.dataset_id,
            "dataset_name": self.name,
            "windowsize": self.windowsize,
        }
        return json_intervals


class IntervalDataTypeEnum(Enum):
    """mapping of data types for front end..."""

    PILEUP = "pileup"
    STACKUP = "stackup"
    LINEPROFILE = "lineprofile"
    LOLA = "lola"
    EMBEDDING_1D = "1d-embedding"
    EMBEDDING_2D = "2d-embedding"


# NOTE some of these functions have no doc string, but most of them are properties or
# declared attrs, adding docstrings here decreases readability
class BaseIntervalData(db.Model):
    """Abstract base class for interval data classes."""

    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(
        db.DateTime,  default=datetime.datetime.utcnow
    )
    name = db.Column(db.String(512), index=True)
    file_path = db.Column(db.String(512), index=True)
    value_type = db.Column(db.String(64))
    binsize = db.Column(db.Integer)
    job_status = db.Column(db.String(64))  # , nullable=False) # success, fail, <job_id>

    @declared_attr
    def intervals_id(cls):
        return db.Column(db.Integer, db.ForeignKey("intervals.id", ondelete="CASCADE"))

    @declared_attr
    def source_intervals(cls):  # FIXME  plural and naming
        return db.relationship("Intervals")

    @property
    @abstractmethod
    def intervaldata_type(self) -> IntervalDataTypeEnum:
        pass

    @declared_attr
    def __mapper_args__(cls):
        """adds the __mapper_args__ dunder var to every object inherting from this
        class. every table inherting needs to be declared as polymorphic"""

        if cls.__name__ != "BaseIntervalData":
            return {"polymorphic_identity": cls.__name__, "concrete": True}
        else:
            return {}

    def __repr__(self):
        """Format print output."""
        return f"<{self.__class__.__name__} {self.name}>"

    def to_json(self):
        """Formats json output."""
        data = {}
        for col in self.__table__.columns:
            data[col] = getattr(self, col.name)
        return data


class AverageIntervalData(BaseIntervalData):
    """db.Table to hold information and pointers to data for
    average values of a dataset at the linked intervals dataset."""

    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(
        db.Integer,
        db.ForeignKey("dataset.id", name="fk_averageivd_dataset", ondelete="CASCADE"),
    )

    @classmethod
    def __declare_last__(cls):
        cls.source_dataset = db.relationship(
            "Dataset", back_populates="averageIntervalData"
        )
        cls.feature = cls.source_dataset

    @property
    def intervaldata_type(self) -> IntervalDataTypeEnum:
        return (
            IntervalDataTypeEnum.PILEUP.value
            if self.value_type in ["Obs/Exp", "ICCF"]
            else IntervalDataTypeEnum.LINEPROFILE.value
        )


class IndividualIntervalData(BaseIntervalData):
    """db.Table to hold information and pointers to data for
    values extracted at each instance held in the linked intervals dataset.
    E.g. for bigwig stack-ups or displaying snipped Hi-C matrices."""

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(
        db.DateTime,  default=datetime.datetime.utcnow
    )
    file_path_small = db.Column(
        db.String(128), index=True
    )  # location of downsampled file
    dataset_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "dataset.id", name="fk_individualivd_dataset", ondelete="CASCADE"
        ),
    )

    @classmethod
    def __declare_last__(cls):
        cls.source_dataset = db.relationship("Dataset")
        cls.feature = cls.source_dataset

    @property
    def intervaldata_type(self) -> IntervalDataTypeEnum:
        return IntervalDataTypeEnum.STACKUP.value


class AssociationIntervalData(BaseIntervalData):
    """db.Table to hold information and pointers to data for values extracted by calculating
    association metrics between dataset collections and intervals. E.g.: LOLA enrichment data,
    Continuous values enrichment."""

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(
        db.DateTime,  default=datetime.datetime.utcnow
    )
    collection_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "collection.id", name="fk_associationivd_collection", ondelete="CASCADE"
        ),
    )

    @classmethod
    def __declare_last__(cls):
        cls.source_collection = db.relationship(
            "Collection", back_populates="associationData"
        )
        cls.feature = cls.source_collection

    @property
    def intervaldata_type(self) -> IntervalDataTypeEnum:
        return IntervalDataTypeEnum.LOLA.value


class EmbeddingIntervalData(BaseIntervalData):
    """db.Table to hold information and pointers to data for values extracted by calculating
    embeddings of intervals based on values in dataset collections and intervals. E.g.: 1D-embeddings based
    on chip-seq data, 2d-embeddings based on Hi-C data."""

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(
        db.DateTime,  default=datetime.datetime.utcnow
    )
    file_path_feature_values = db.Column(db.String(512), index=True)
    thumbnail_path = db.Column(db.String(512), index=True)
    cluster_id_path = db.Column(db.String(512), index=True)
    feature_distribution_path = db.Column(db.String(512), index=True)
    normalization = db.Column(db.String(64))
    cluster_number = db.Column(db.String(64))
    collection_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "collection.id", name="fk_embeddingivd_collection", ondelete="CASCADE"
        ),
    )
    dataset_id = db.Column(
        db.Integer,
        db.ForeignKey("dataset.id", name="fk_embeddingivd_dataset", ondelete="CASCADE"),
    )

    @classmethod
    def __declare_last__(cls):
        cls.source_dataset = db.relationship("Dataset", back_populates="embeddingData")
        cls.source_collection = db.relationship(
            "Collection", back_populates="embeddingData"
        )

    @property
    def feature(self):
        """as embeddings can be 1d or 2d feature is set dynamically"""
        return self.source_dataset if self.source_dataset else self.source_collection

    @property
    def intervaldata_type(self) -> IntervalDataTypeEnum:
        return (
            IntervalDataTypeEnum.EMBEDDING_2D.value
            if self.value_type == "2d-embedding"
            else IntervalDataTypeEnum.EMBEDDING_1D.value
        )


class Task(db.Model):
    """Models the tasks dispatched to the redis queue."""

    id = db.Column(db.String(36), primary_key=True)
    created_at = db.Column(
        db.DateTime,  default=datetime.datetime.utcnow
    )
    name = db.Column(db.String(512), index=True)
    description = db.Column(db.String(512))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    dataset_id = db.Column(db.Integer, db.ForeignKey("dataset.id"))
    collection_id = db.Column(db.Integer, db.ForeignKey("collection.id"))
    intervals_id = db.Column(db.Integer, db.ForeignKey("intervals.id"))
    complete = db.Column(db.Boolean, default=False)

    @staticmethod
    def filter_failed_tasks(tasks):
        """Returns failed tasks of the tasks provided"""
        output = []
        for task in tasks:
            if task.get_rq_job() is None:
                output.append(task)
                continue
            if task.get_rq_job().get_status() == "failed":
                output.append(task)
        return output

    def get_rq_job(self):
        """Fetches the rq job of the task"""
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job

    def get_progress(self):
        """Fetches the progress of the rq job"""
        job = self.get_rq_job()
        return job.meta.get("progress", 0) if job is not None else 100


# DO NOT REMOVE
# class Task(db.Model):
#     """Models the tasks dispatched to the redis queue."""

#     #id = db.Column(db.String(36), primary_key=True)
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

#     func = db.Column(db.String(512))
#     progress = db.Column(db.Integer, default=0)
#     status = db.Column(db.String(64), default='none') # running, failed, finished
#     args = db.Column(db.JSON)

#     user = db.relationship("User")

#     @property
#     def complete(self):
#         return self.progress == 100

#     @staticmethod
#     def filter_failed_tasks(tasks):
#         """Returns failed tasks of the tasks provided"""
#         output = []
#         for task in tasks:
#             if task.get_rq_job() is None:
#                 output.append(task)
#                 continue
#             if task.get_rq_job().get_status() == "failed":
#                 output.append(task)
#         return output

#     def get_rq_job(self):
#         """Fetches the rq job of the task"""
#         try:
#             return rq.job.Job.fetch(self.id, connection=current_app.redis)
#         except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
#             return None

#     def get_progress(self):
#         """Fetches the progress of the rq job"""
#         job = self.get_rq_job()
#         return job.meta.get("progress", 0) if job is not None else 100

#     @staticmethod
#     def create(func, user: User, commit=True, *args, **kwargs):
#         args_dict = {}
#         args_dict['unnamed'] = args
#         args_dict['named'] = dict(kwargs)
#         task = Task(
#             func=func.__qualname__,
#             user=user,
#             args=args_dict
#         )
#         db.session.add(task)
#         if commit:
#             db.session.commit()
#         return task

#     def launch(self, queue=None): # TODO give this a go
#         if queue is None:
#             return self._run_task()
#         else:
#             def wrap_with_app_context(self: Task):
#                 # make app context
#                 from . import create_app
#                 app = create_app(os.getenv("FLASK_CONFIG") or "default")
#                 app.app_context().push()
#                 self._run_task()
#                 # TODO redis worker exception handling

#             queue.enqueue(
#                 wrap_with_app_context,
#                 job_id = self.id,
#                 task = self
#             )

#     def _run_task(self):
#         self.status = 'running'
#         db.session.commit()
#         try:
#             return_value = self.stored_function(
#                 *self.args['unnamed'],
#                 **self.args['named']
#             )
#             self.status = 'success'
#             db.session.commit()
#             return return_value
#         except Exception as err:
#             self.status = 'failed'
#             db.session.commit()
#             raise err

#     @property
#     def stored_function(self):
#         module_name, func_name = self.func.rsplit('.',1)
#         module = importlib.import_module(module_name)
#         func = getattr(module, func_name)
#         return func


class BedFileMetadata(db.Model):
    """Models the associated with a bedfile"""

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(
        db.DateTime, default=datetime.datetime.utcnow
    )
    name = db.Column(db.String(512))
    file_path = db.Column(db.String(512))
    metadata_fields = db.Column(db.String(1024))
    dataset_id = db.Column(
        db.Integer, db.ForeignKey("dataset.id")
    )  # intervals over which the values were extracted

    def __repr__(self):
        """Format print output."""
        return f"<Metadata {self.name}>"


class Session(db.Model):
    """Model for session data that represents configurations
    of views. For example, compare views."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    session_object = db.Column(db.Text(10**9))
    created_utc = db.Column(
        db.DateTime, nullable=False, default=datetime.datetime.utcnow
    )
    session_type = db.Column(db.String(100))
    datasets = db.relationship("Dataset", secondary=session_dataset_assoc_table)
    collections = db.relationship(
        "Collection", secondary=session_collection_assoc_table
    )

    def generate_session_token(self):
        """Generates session token"""
        serializer = JSONWebSignatureSerializer(current_app.config["SECRET_KEY"])
        return serializer.dumps({"session_id": self.id}).decode("utf-8")

    @staticmethod
    def verify_auth_token(token):
        """Verifies the session token"""
        serializer = JSONWebSignatureSerializer(current_app.config["SECRET_KEY"])
        try:
            data = serializer.loads(token)
        except:
            return None
        return Session.query.get(data["session_id"])

    def to_json(self):
        """Formats json output."""
        json_session = {
            "id": self.id,
            "name": self.name,
            "created": self.created_utc.strftime("%m/%d/%Y, %H:%M:%S"),
            "session_type": self.session_type,
            "session_object": self.session_object,
        }
        return json_session

    def __repr__(self):
        """Format print output."""
        return f"<Session {self.name}>"


# This maps abstract tables to other tables
db.configure_mappers()

# helpers


def all_tasks_finished(tasks):
    """Returns True if all rq jobs are finished."""
    for task in tasks:
        job = task.get_rq_job()
        if job is None:
            # if job is not in queue anymore, it finished successfully
            continue
        if not job.is_finished:
            return False
    return True


def any_tasks_failed(tasks):
    """Return True if any rq job failed."""
    for task in tasks:
        if task.get_rq_job() is None:
            # job is not available in rq anymore
            continue
        else:
            if task.get_rq_job().get_status() == "failed":
                return True
    return False


def _rq_job_wrapper(func, *args, **kwargs):
    import app

    curr_app = app.create_app(os.getenv("FLASK_CONFIG") or "default")
    app_context = curr_app.app_context()
    app_context.push()
    return func(*args, **kwargs)
