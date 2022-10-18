"""Database models for HiCognition."""
# TODO refactor to allow database to not know about flask-server or similar
# TODO task launcher: why put it into the user class?

import datetime
from typing_extensions import Required
from flask.globals import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import inspect
import pandas as pd
import cooler
import json
import os
from hicognition.utils import parse_binsizes
from hicognition.format_checkers import FORMAT_CHECKERS
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import JSONWebSignatureSerializer
import rq
import hicognition
import redis
from . import db
from sqlalchemy import Column, Integer, ForeignKey, String, Enum, Table, UniqueConstraint, Boolean, Text, DateTime


# define association tables

session_dataset_assoc_table = Table(
    "session_dataset_assoc_table",
    Column("session_id", Integer, ForeignKey("db.session.id")),
    Column("dataset_id", Integer, ForeignKey("dataset.id")),
)

session_collection_assoc_table = Table(
    "session_collection_assoc_table",
    Column("session_id", Integer, ForeignKey("db.session.id")),
    Column("collection_id", Integer, ForeignKey("collection.id")),
)

dataset_collection_assoc_table = Table(
    "dataset_collection_assoc_table",
    Column("collection_id", Integer, ForeignKey("collection.id")),
    Column("dataset_id", Integer, ForeignKey("dataset.id")),
)

dataset_preprocessing_table = Table(
    "dataset_dataset_preprocessing_table",
    Column("dataset_region", Integer, ForeignKey("dataset.id")),
    Column("dataset_feature", Integer, ForeignKey("dataset.id")),
    UniqueConstraint("dataset_region", "dataset_feature", name="uix_1"),
)

dataset_failed_table = Table(
    "dataset_failed_table",
    Column("dataset_region", Integer, ForeignKey("dataset.id")),
    Column("dataset_feature", Integer, ForeignKey("dataset.id")),
    UniqueConstraint("dataset_region", "dataset_feature", name="uix_1"),
)

dataset_completed_table = Table(
    "dataset_completed_table",
    Column("dataset_region", Integer, ForeignKey("dataset.id")),
    Column("dataset_feature", Integer, ForeignKey("dataset.id")),
    UniqueConstraint("dataset_region", "dataset_feature", name="uix_1"),
)

collections_preprocessing_table = Table(
    "collections_preprocessing_table",
    Column("dataset_region", Integer, ForeignKey("dataset.id")),
    Column("collection_feature", Integer, ForeignKey("collection.id")),
    UniqueConstraint("dataset_region", "collection_feature", name="uix_1"),
)

collections_failed_table = Table(
    "collections_failed_table",
    Column("dataset_region", Integer, ForeignKey("dataset.id")),
    Column("collection_feature", Integer, ForeignKey("collection.id")),
    UniqueConstraint("dataset_region", "collection_feature", name="uix_1"),
)


class User(db.Model, UserMixin):
    """User database model"""

    id = Column(Integer, primary_key=True)
    username = Column(String(64), index=True, unique=True)
    email = Column(String(120), index=True, unique=True)
    password_hash = Column(String(128))
    datasets = db.relationship(
        "Dataset", backref="owner", lazy="dynamic", cascade="all, delete-orphan"
    )
    tasks = db.relationship(
        "Task", backref="user", lazy="dynamic", cascade="all, delete-orphan"
    )
    credentials = db.relationship(
        "User_DataRepository_Credentials",
        backref="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def add_repository_credentials(
        self, repository_name: str, key: str, secret: str
    ):  # TODO needed?
        credentials = User_DataRepository_Credentials(
            self.id, repository_name, key, secret
        )
        db.db.session.add(credentials)
        return credentials

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

    def launch_task(self, queue, name, description, dataset_id, *args, **kwargs):
        """adds task to queue"""

        rq_job = queue.enqueue(
            "app.tasks." + name, dataset_id, job_timeout="10h", *args, **kwargs
        )

        # check whether intervals_id is in kwargs
        if "intervals_id" in kwargs:
            intervals_id = kwargs["intervals_id"]
        else:
            intervals_id = None
        task = Task(
            id=rq_job.get_id(),
            name=name,
            description=description,
            user_id=self.id,
            dataset_id=dataset_id,
            intervals_id=intervals_id,
        )
        db.session.add(task)
        return task

    def launch_collection_task(
        self, queue, name, description, collection_id, *args, **kwargs
    ):
        """adds task based on collection to queue"""
        rq_job = queue.enqueue(
            "app.tasks." + name, collection_id, job_timeout="10h", *args, **kwargs
        )
        # check whether inverals_id is in kwargs
        if "intervals_id" in kwargs:
            intervals_id = kwargs["intervals_id"]
        else:
            intervals_id = None
        task = Task(
            id=rq_job.get_id(),
            name=name,
            description=description,
            user_id=self.id,
            collection_id=collection_id,
            intervals_id=intervals_id,
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


# class User_ExternSource mtm
# TODO replace with better name?
class DataRepository(db.Model):
    """Model for external data repositories.
    Name is primary key, as this table will hold only a few rows and it makes
    handling gets/posts easier.

    url must contain an {href} tag.
    file_url must contain the {id} tag.
    """

    # fields
    name = Column(String(64), nullable=False, primary_key=True)
    url = Column(String(512), default="")
    file_url = Column(String(512), default="")
    auth_required = Column(Boolean, default=False)

    def build_url_sample(self, data_id: str):
        return self.file_url.format(id=data_id)

    def build_url(self, href: str):
        return self.url.format(href=href)

    credentials = db.relationship(
        "User_DataRepository_Credentials",
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


class User_DataRepository_Credentials(db.Model):  # TODO change name
    """Optional many-to-many object to store user keys for external repos"""

    # fields
    user_id = Column(ForeignKey("user.id"), primary_key=True)
    repository_name = Column(ForeignKey("data_repository.name"), primary_key=True)
    key = Column(String(512), nullable=False)
    secret = Column(String(512), nullable=False)

    # assoc
    # user = db.relationship("User", back_populates='credentials')
    repository = db.relationship("DataRepository", back_populates="credentials")

class DatasetProcessingTasks(db.Model):
    region_id = Column(Integer, ForeignKey("task.id"), primary_key=True)
    feature_id = Column(Integer, ForeignKey("dataset.id"), primary_key=True)
    status = Column(Enum('processing', 'success', 'failed'))
    
    __table_args__ = UniqueConstraint("dataset_region", "dataset_feature", name="uix_1")

class DatasetMetadata(db.Model):
    dataset_id = Column(Integer, ForeignKey("dataset.id"))
    key = Column(String(128), required=True)
    value = Column(String(128), required=True)

class Dataset(db.Model):
    """Dataset database model"""
    # fields
    id = Column(Integer, primary_key=True)
    assembly_id = Column(Integer, ForeignKey("assembly.id"))
    user_id = Column(Integer, ForeignKey("user.id"))
    
    name = Column(String(512), required=True)
    description = Column(String(81))
    size_type = Column(Enum('interval', 'point'), required=True)
    value_type = Column(String(128), required=True)
    file_path = Column(String(512), required=True)
    public = Column(Boolean, required=True, default=False)
    filetype = Column(Enum('bedfile', 'bigwig', 'cooler'), required=True)
    upload_state = Column(Enum('new', 'uploading', 'uploaded', 'upload_failed'), required=True, default='new')

    # these i would remove => we don't have to save them
    repository_name = Column(ForeignKey("data_repository.name"), nullable=True) 
    sample_id = Column(String(128), nullable=True)
    source_url = Column(String(512), nullable=True)

    # metadata goes into metadata
    # perturbation = db.Column(db.String(64), default="undefined")
    # cellCycleStage = db.Column(db.String(64), default="undefined")
    # method = Column(String(64), default="undefined")
    # normalization = Column(String(64), default="undefined")
    # derivationType = Column(String(64), default="undefined")
    # protein = Column(String(64), default="undefined")
    # directionality = Column(String(64), default="undefined")
    metadata = db.relationship("DatasetMetadata", cascade="all, delete-orphan")
    
    # unused
    # available_binsizes = Column(String(500), default="undefined")
    
    
    # self db.relationships
    # this one is hard: during delete it is checked if there are tasks going that use this feature.
    # how to know if there are features processed if there are no tasks?
    processing_state = Column(Enum('idle', 'processing', 'processing_failed'), required=True, default='new') 
    
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
    # db.relationships
    intervals = db.relationship(
        "Intervals",
        backref="source_dataset",
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
        backref="source_dataset",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    individualIntervalData = db.relationship(
        "IndividualIntervalData",
        backref="source_dataset",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    embeddingData = db.relationship(
        "EmbeddingIntervalData",
        backref="source_dataset",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    bedFileMetadata = db.relationship(
        "BedFileMetadata",
        backref="associated_dataset",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    tasks = db.relationship("Task", backref="dataset", lazy="dynamic")
    repository = db.relationship("DataRepository")
    user = db.relationship("User")

    def get_tasks_in_progress(self):
        """Gets the tasks in progress for the dataset."""
        return Task.query.filter_by(dataset=self, complete=False).all()

    def __repr__(self):
        """Format print output."""
        return f"<Dataset {self.dataset_name}>"

    ## not used
    # def set_processing_state(self, database):
    #     """sets the current processing state of the dataset instance.
    #     Launching task sets processing state, this sets finished/failed state"""
    #     if self.processing_state not in ["processing", "finished", "failed"]:
    #         return
    #     # check if there are any unfinished tasks
    #     tasks = self.tasks.filter(Task.complete.is_(False)).all()
    #     if len(tasks) == 0:
    #         self.processing_state = "finished"
    #     else:
    #         if all_tasks_finished(tasks):
    #             self.processing_state = "finished"
    #         elif any_tasks_failed(tasks):
    #             self.processing_state = "failed"
    #         else:
    #             self.processing_state = "processing"
    #     database.db.session.add(self)
    #     database.db.session.commit()

    ## do in upper layer
    # def is_access_denied(self, app_context):
    #     """Determine whether context
    #     allows access to dataset."""
    #     if current_app.config["SHOWCASE"]:
    #         return False
    #     if self.public:
    #         return False
    #     if (self.user_id != app_context.current_user.id) and (
    #         self.id not in app_context.session_datasets
    #     ):
    #         return True
    #     return False

    ## do in upper layer
    # def add_fields_from_form(self, form, requirement_spec=None):
    #     """Adds values for fields from form"""
    #     if requirement_spec is None:
    #         requirement_spec = self.DATASET_META_FIELDS_NEW
    #     for form_key, dataset_field in requirement_spec.items():
    #         if form_key in form:
    #             if form_key == "public":
    #                 self.__setattr__(
    #                     dataset_field,
    #                     "public" in form and form["public"].lower() == "true",
    #                 )
    #             else:
    #                 self.__setattr__(dataset_field, form[form_key])

    ## do in upper layer (copy this dataset, then change)
    # def add_fields_from_dataset(self, other_dataset):
    #     """adds metadata from other dataset"""
    #     for dataset_field in self.DATASET_META_FIELDS.values():
    #         if other_dataset.__getattribute__(dataset_field) is not None:
    #             self.__setattr__(
    #                 dataset_field, other_dataset.__getattribute__(dataset_field)
    #             )

    ## this is only used by put_routes/modify_dataset => upper layer or leave out
    # def blank_fields(self):
    #     """Blanks dataset fields"""
    #     # common fields
    #     for field in self.COMMON_REQUIRED_KEYS:
    #         self.__setattr__(field, "undefined")
    #     # metadata_fields
    #     for key in self.DATASET_META_FIELDS_MODIFY.keys():
    #         if key == "public":
    #             continue
    #         self.__setattr__(key, "undefined")

    ## put on upper level or do differently:
    ### modify dataset, but do not commit
    ### then validate dataset and have this (or similar function called)
    ### do not use form data
    # @classmethod
    # def modify_dataset_requirements_fulfilled(cls, form, filetype):
    #     """Checks whether all fields that are needed to modiy a dataset are fulfilled"""
    #     form_keys = set(form.keys())
    #     if any(key not in form_keys for key in cls.COMMON_REQUIRED_KEYS):
    #         return False
    #     # check metadata
    #     dataset_type_mapping = current_app.config["DATASET_OPTION_MAPPING"][
    #         "DatasetType"
    #     ]
    #     value_types = dataset_type_mapping[filetype]["ValueType"]
    #     if form["ValueType"] not in value_types.keys():
    #         return False
    #     # check value type members
    #     for key, possible_values in value_types[form["ValueType"]].items():
    #         # skip size type
    #         if key == "SizeType":
    #             continue
    #         if key not in form_keys:
    #             return False
    #         # check whether field is freetext
    #         if possible_values == "freetext":
    #             continue
    #         # check that value in form corresponds to possible values
    #         if form[key] not in possible_values:
    #             return False
    #     # check whether there is a field that is unsuitable
    #     for key in cls.ADD_REQUIRED_KEYS + ["SizeType"]:
    #         if key in form_keys:
    #             return False
    #     return True

    ### implement rmfiles functions for every subsequent data entry
    def rmfiles(self):
        pass
    
    
    
    def delete_data_of_associated_entries(self):
        """deletes files of associated entries"""
        intervals = []
        average_interval_data = []
        individual_interval_data = []
        embedding_interval_data = []
        metadata = []
        # cooler only needs deletion of derived averageIntervalData
        if self.filetype == "cooler":
            average_interval_data = AverageIntervalData.query.filter(
                AverageIntervalData.dataset_id == self.id
            ).all()
            embedding_interval_data = EmbeddingIntervalData.query.filter(
                EmbeddingIntervalData.dataset_id == self.id
            ).all()
        # bedfile needs deletion of intervals and averageIntervalData
        if self.filetype == "bedfile":
            intervals = Intervals.query.filter(Intervals.dataset_id == self.id).all()
            average_interval_data = AverageIntervalData.query.filter(
                AverageIntervalData.intervals_id.in_([entry.id for entry in intervals])
            ).all()
            individual_interval_data = IndividualIntervalData.query.filter(
                IndividualIntervalData.intervals_id.in_(
                    [entry.id for entry in intervals]
                )
            ).all()
            embedding_interval_data = EmbeddingIntervalData.query.filter(
                EmbeddingIntervalData.intervals_id.in_(
                    [entry.id for entry in intervals]
                )
            ).all()
            metadata = BedFileMetadata.query.filter(
                BedFileMetadata.dataset_id == self.id
            ).all()
        if self.filetype == "bigwig":
            average_interval_data = AverageIntervalData.query.filter(
                AverageIntervalData.dataset_id == self.id
            ).all()
            individual_interval_data = IndividualIntervalData.query.filter(
                IndividualIntervalData.dataset_id == self.id
            ).all()
        # delete files and remove from database
        deletion_queue = (
            [self]
            + intervals
            + average_interval_data
            + individual_interval_data
            + embedding_interval_data
            + metadata
        )
        for entry in deletion_queue:
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
            database.db.session.delete(task)
        database.db.session.commit()

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
        if self.filetype == "bedfile":
            self.user.launch_task(  #  TODO current user or dataset owner user?
                current_app.queues["short"],
                "pipeline_bed",
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

        # db.session.commit()

    def to_json(self):
        """Generates a JSON from the model"""
        json_dataset = {}
        for key in inspect(Dataset).columns.keys():
            if key == "processing_id":
                continue
            value = self.__getattribute__(key)
            if value != "undefined":
                json_dataset[key] = value
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

    id = Column(Integer, primary_key=True)
    name = Column(String(1024))
    user_id = Column(Integer, ForeignKey("user.id"))
    public = Column(Boolean, default=False)
    kind = Column(
        String(256)
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
        backref="source_collection",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    embeddingData = db.relationship(
        "EmbeddingIntervalData",
        backref="source_collection",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    processing_state = Column(String(64))

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
        assoc_data = self.associationData.all()
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
        database.db.session.add(self)
        database.db.session.commit()

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
            database.db.session.delete(task)
        database.db.session.commit()

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

    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, ForeignKey("dataset.id"))
    binsize = Column(Integer, index=True)
    filepath = Column(String(512), index=True)


class Organism(db.Model):
    """Organism table for genome assembly"""

    id = Column(Integer, primary_key=True)
    name = Column(String(512))
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

    id = Column(Integer, primary_key=True)
    name = Column(String(512))
    chrom_sizes = Column(String(512), index=True)
    chrom_arms = Column(String(512), index=True)
    organism_id = Column(Integer, ForeignKey("organism.id"))
    user_id = Column(Integer, ForeignKey("user.id"))

    def to_json(self):
        """Generates json output."""
        json_dataset = {"id": self.id, "name": self.name, "user_id": self.user_id}
        return json_dataset


class Intervals(db.Model):
    """Genomic IntervalData database model"""

    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, ForeignKey("dataset.id"))
    name = Column(String(512), index=True)
    file_path_sub_sample_index = Column(String(512), index=True)
    windowsize = Column(Integer, index=True)
    averageIntervalData = db.relationship(
        "AverageIntervalData",
        backref="source_intervals",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    individualIntervalData = db.relationship(
        "IndividualIntervalData",
        backref="source_intervals",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    associationIntervalData = db.relationship(
        "AssociationIntervalData",
        backref="source_intervals",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    embeddingIntervalData = db.relationship(
        "EmbeddingIntervalData",
        backref="source_intervals",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    tasks = db.relationship(
        "Task", backref="intervals", lazy="dynamic", cascade="all, delete-orphan"
    )

    def get_associated_preprocessed_datasets(self):
        """returns all associated datasets"""
        return (
            self.averageIntervalData.all()
            + self.individualIntervalData.all()
            + self.associationIntervalData.all()
            + self.embeddingIntervalData.all()
        )

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


class AverageIntervalData(db.Model):
    """Table to hold information and pointers to data for
    average values of a dataset at the linked intervals dataset."""

    id = Column(Integer, primary_key=True)
    binsize = Column(Integer)
    name = Column(String(512), index=True)
    file_path = Column(String(512), index=True)
    value_type = Column(String(64))
    dataset_id = Column(Integer, ForeignKey("dataset.id"))
    intervals_id = Column(Integer, ForeignKey("intervals.id"))

    def add_to_preprocessed_dataset_map(self, preprocessed_dataset_map):
        """Adds self to preprocessed dataset map"""
        dataset = Dataset.query.get(self.dataset_id)
        # check whether there are any uncompleted tasks for the region dataset associated with these features
        interval = Intervals.query.get(self.intervals_id)
        region_dataset = interval.source_dataset
        # check whether region_dataset is interval
        if region_dataset.sizeType == "Interval":
            windowsize = "variable"
        else:
            windowsize = interval.windowsize
        # check whether dataset is in failed or processing datasets
        if (dataset in region_dataset.processing_features) or (
            dataset in region_dataset.failed_features
        ):
            return
        if self.value_type in ["Obs/Exp", "ICCF"]:
            preprocessed_dataset_map["pileup"][dataset.id][
                "name"
            ] = dataset.dataset_name
            preprocessed_dataset_map["pileup"][dataset.id]["data_ids"][windowsize][
                self.binsize
            ][self.value_type] = str(self.id)
        else:
            preprocessed_dataset_map["lineprofile"][dataset.id][
                "name"
            ] = dataset.dataset_name
            preprocessed_dataset_map["lineprofile"][dataset.id]["data_ids"][windowsize][
                self.binsize
            ] = str(self.id)

    def __repr__(self):
        """Format print output."""
        return f"<AverageIntervalData {self.name}>"

    def to_json(self):
        """Formats json output."""
        json_average_interval_data = {
            "id": self.id,
            "binsize": self.binsize,
            "name": self.name,
            "file_path": self.file_path,
            "dataset_id": self.dataset_id,
            "intervals_id": self.intervals_id,
            "value_type": self.value_type,
        }
        return json_average_interval_data


class IndividualIntervalData(db.Model):
    """Table to hold information and pointers to data for
    values extracted at each instance held in the linked intervals dataset.
    E.g. for bigwig stack-ups or displaying snipped Hi-C matrices."""

    id = Column(Integer, primary_key=True)
    binsize = Column(Integer)
    name = Column(String(512), index=True)
    file_path = Column(String(512), index=True)
    file_path_small = Column(
        String(128), index=True
    )  # location of downsampled file
    dataset_id = Column(
        Integer, ForeignKey("dataset.id")
    )  # dataset, which was used for value extraction
    intervals_id = Column(
        Integer, ForeignKey("intervals.id")
    )  # intervals over which the values were extracted

    def add_to_preprocessed_dataset_map(self, preprocessed_dataset_map):
        """Adds self to preprocessed dataset map"""
        dataset = Dataset.query.get(self.dataset_id)
        # check whether there are any uncompleted tasks for the feature dataset
        interval = Intervals.query.get(self.intervals_id)
        region_dataset = interval.source_dataset
        # check whether region_dataset is interval
        if region_dataset.sizeType == "Interval":
            windowsize = "variable"
        else:
            windowsize = interval.windowsize
        # check whether dataset is in failed or processing datasets
        if (dataset in region_dataset.processing_features) or (
            dataset in region_dataset.failed_features
        ):
            return
        preprocessed_dataset_map["stackup"][dataset.id]["name"] = dataset.dataset_name
        preprocessed_dataset_map["stackup"][dataset.id]["data_ids"][windowsize][
            self.binsize
        ] = str(self.id)

    def __repr__(self):
        """Format print output."""
        return f"<IndividualIntervalData {self.name}>"

    def to_json(self):
        """Formats json output."""
        json_individual_interval_data = {
            "id": self.id,
            "binsize": self.binsize,
            "name": self.name,
            "file_path": self.file_path,
            "dataset_id": self.dataset_id,
            "intervals_id": self.intervals_id,
        }
        return json_individual_interval_data


class AssociationIntervalData(db.Model):
    """Table to hold information and pointers to data for values extracted by calculating
    association metrics between dataset collections and intervals. E.g.: LOLA enrichment data,
    Continuous values enrichment."""

    id = Column(Integer, primary_key=True)
    binsize = Column(Integer)
    name = Column(String(512), index=True)
    file_path = Column(String(512), index=True)
    value_type = Column(String(64))
    collection_id = Column(Integer, ForeignKey("collection.id"))
    intervals_id = Column(Integer, ForeignKey("intervals.id"))

    def add_to_preprocessed_dataset_map(self, preprocessed_dataset_map):
        """Adds self to preprocessed dataset map"""
        collection = Collection.query.get(self.collection_id)
        interval = Intervals.query.get(self.intervals_id)
        region_dataset = interval.source_dataset
        # check whether region_dataset is interval
        if region_dataset.sizeType == "Interval":
            windowsize = "variable"
        else:
            windowsize = interval.windowsize
        if (collection in region_dataset.processing_collections) or (
            collection in region_dataset.failed_collections
        ):
            return
        preprocessed_dataset_map["lola"][collection.id]["name"] = collection.name
        preprocessed_dataset_map["lola"][collection.id][
            "collection_dataset_names"
        ] = collection.to_json()["dataset_names"]
        preprocessed_dataset_map["lola"][collection.id]["data_ids"][windowsize][
            self.binsize
        ] = str(self.id)


class EmbeddingIntervalData(db.Model):
    """Table to hold information and pointers to data for values extracted by calculating
    embeddings of intervals based on values in dataset collections and intervals. E.g.: 1D-embeddings based
    on chip-seq data, 2d-embeddings based on Hi-C data."""

    id = Column(Integer, primary_key=True)
    binsize = Column(Integer)
    name = Column(String(512), index=True)
    file_path = Column(String(512), index=True)
    file_path_feature_values = Column(String(512), index=True)
    thumbnail_path = Column(String(512), index=True)
    cluster_id_path = Column(String(512), index=True)
    feature_distribution_path = Column(String(512), index=True)
    value_type = Column(String(64))
    normalization = Column(String(64))
    cluster_number = Column(String(64))
    collection_id = Column(Integer, ForeignKey("collection.id"))
    dataset_id = Column(Integer, ForeignKey("dataset.id"))
    intervals_id = Column(Integer, ForeignKey("intervals.id"))

    def _add_1d_to_preprocessed_dataset_map(self, preprocessed_dataset_map):
        """Adds self if 1d embedding"""
        collection = Collection.query.get(self.collection_id)
        # check whether there are any uncompleted tasks for the feature dataset
        interval = Intervals.query.get(self.intervals_id)
        region_dataset = interval.source_dataset
        # check whether region_dataset is interval
        if region_dataset.sizeType == "Interval":
            windowsize = "variable"
        else:
            windowsize = interval.windowsize
        if (collection in region_dataset.processing_collections) or (
            collection in region_dataset.failed_collections
        ):
            return
        preprocessed_dataset_map["embedding1d"][collection.id]["name"] = collection.name
        preprocessed_dataset_map["embedding1d"][collection.id][
            "collection_dataset_names"
        ] = collection.to_json()["dataset_names"]
        preprocessed_dataset_map["embedding1d"][collection.id]["data_ids"][windowsize][
            self.binsize
        ][self.cluster_number] = str(self.id)

    def _add_2d_to_preprocessed_dataset_map(self, preprocessed_dataset_map):
        """Adds self if 2d embedding"""
        dataset = Dataset.query.get(self.dataset_id)
        # check whether there are any uncompleted tasks for the feature dataset
        interval = Intervals.query.get(self.intervals_id)
        region_dataset = interval.source_dataset
        # check whether region_dataset is interval
        if region_dataset.sizeType == "Interval":
            windowsize = "variable"
        else:
            windowsize = interval.windowsize
        if (dataset in region_dataset.processing_features) or (
            dataset in region_dataset.failed_features
        ):
            return
        preprocessed_dataset_map["embedding2d"][dataset.id][
            "name"
        ] = dataset.dataset_name
        preprocessed_dataset_map["embedding2d"][dataset.id]["data_ids"][windowsize][
            self.binsize
        ][self.normalization][self.cluster_number] = str(self.id)

    def add_to_preprocessed_dataset_map(self, preprocessed_dataset_map):
        """Add self to preprocesse dataset_map"""
        if self.value_type == "2d-embedding":
            self._add_2d_to_preprocessed_dataset_map(preprocessed_dataset_map)
        else:
            self._add_1d_to_preprocessed_dataset_map(preprocessed_dataset_map)


class Task(db.Model):
    """Models the tasks dispatched to the redis queue."""

    id = Column(String(36), primary_key=True)
    name = Column(String(512), index=True)
    description = Column(String(512))
    user_id = Column(Integer, ForeignKey("user.id"))
    dataset_id = Column(Integer, ForeignKey("dataset.id"))
    collection_id = Column(Integer, ForeignKey("collection.id"))
    intervals_id = Column(Integer, ForeignKey("intervals.id"))
    complete = Column(Boolean, default=False)

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


class BedFileMetadata(db.Model):
    """Models the associated with a bedfile"""

    id = Column(Integer, primary_key=True)
    name = Column(String(512))
    file_path = Column(String(512))
    metadata_fields = Column(String(1024))
    dataset_id = Column(
        Integer, ForeignKey("dataset.id")
    )  # intervals over which the values were extracted

    def __repr__(self):
        """Format print output."""
        return f"<Metadata {self.name}>"


class Session(db.Model):
    """Model for session data that represents configurations
    of views. For example, compare views."""

    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    user_id = Column(Integer, ForeignKey("user.id"))
    session_object = Column(Text(10**9))
    created_utc = Column(
        DateTime, nullable=False, default=datetime.datetime.utcnow
    )
    session_type = Column(String(100))
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
        return db.session.query.get(data["session_id"])

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
