"""Database models for HiCognition."""
import datetime
from flask.globals import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import JSONWebSignatureSerializer
from flask_login import UserMixin
import redis
import rq
from app import db, login


class User(db.Model, UserMixin):
    """User database model"""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    datasets = db.relationship("Dataset", backref="owner", lazy="dynamic")
    tasks = db.relationship("Task", backref="user", lazy="dynamic")

    def set_password(self, password):
        """set password helper."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """check password helper."""
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expiration):
        """generates authentication token"""
        s = Serializer(current_app.config["SECRET_KEY"], expires_in=expiration)
        return s.dumps({"id": self.id}).decode("utf-8")

    def launch_task(self, name, description, dataset_id, *args, **kwargs):
        rq_job = current_app.task_queue.enqueue(
            "app.tasks." + name, dataset_id, job_timeout="10h", *args, **kwargs
        )
        task = Task(
            id=rq_job.get_id(),
            name=name,
            description=description,
            user_id=self.id,
            dataset_id=dataset_id,
        )
        db.session.add(task)
        return task

    def get_tasks_in_progress(self):
        return Task.query.filter_by(user=self, complete=False).all()

    def get_task_in_progress(self, name):
        return Task.query.filter_by(name=name, user=self, complete=False).first()

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data["id"])

    def __repr__(self):
        """Format print output."""
        return "<User {}>".format(self.username)


class Dataset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dataset_name = db.Column(db.String(64), index=True)
    genotype = db.Column(db.String(64), default="undefined")
    description = db.Column(db.String(81), default="undefined")
    file_path = db.Column(db.String(128), index=True)
    public = db.Column(db.Boolean, default=False)
    filetype = db.Column(db.String(64), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    available_binsizes = db.Column(db.String(500))
    intervals = db.relationship("Intervals", backref="source_dataset", lazy="dynamic")
    averageIntervalData = db.relationship(
        "AverageIntervalData", backref="source_dataset", lazy="dynamic"
    )
    individualIntervalData = db.relationship(
        "IndividualIntervalData", backref="source_dataset", lazy="dynamic"
    )
    bedFileMetadata = db.relationship(
        "BedFileMetadata", backref="associated_dataset", lazy="dynamic"
    )
    tasks = db.relationship("Task", backref="dataset", lazy="dynamic")
    processing_state = db.Column(db.String(64))

    def get_tasks_in_progress(self):
        return Task.query.filter_by(dataset=self, complete=False).all()

    def __repr__(self):
        """Format print output."""
        return f"<Dataset {self.dataset_name}>"

    def set_processing_state(self, db):
        """sets the current processing state of the dataset instance.
        Launching task sets processing state, this sets finished/failed state"""
        if self.processing_state not in ["processing", "finished", "failed"]:
            return
        # check if there are any unfinished tasks
        tasks = self.tasks.filter(Task.complete == False).all()
        if len(tasks) == 0:
            self.processing_state = "finished"
        else:
            if all_tasks_finished(tasks):
                self.processing_state = "finished"
            elif any_tasks_failed(tasks):
                self.processing_state = "failed"
            else:
                self.processing_state = "processing"
        db.session.add(self)
        db.session.commit()

    def to_json(self):
        json_dataset = {
            "id": self.id,
            "dataset_name": self.dataset_name,
            "genotype": self.genotype,
            "description": self.description,
            "file_path": self.file_path,
            "filetype": self.filetype,
            "user_id": self.user_id,
            "processing_state": self.processing_state,
            "public": self.public,
        }
        return json_dataset


class Intervals(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey("dataset.id"))
    name = db.Column(db.String(64), index=True)
    file_path = db.Column(db.String(128), index=True)
    file_path_sub_sample_index = db.Column(db.String(128), index=True)
    windowsize = db.Column(db.Integer, index=True)
    averageIntervalData = db.relationship(
        "AverageIntervalData", backref="source_intervals", lazy="dynamic"
    )
    individualIntervalData = db.relationship(
        "IndividualIntervalData", backref="source_intervals", lazy="dynamic"
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
            "file_path": self.file_path,
            "windowsize": self.windowsize,
        }
        return json_intervals


class AverageIntervalData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    binsize = db.Column(db.Integer)
    name = db.Column(db.String(64), index=True)
    file_path = db.Column(db.String(128), index=True)
    value_type = db.Column(db.String(64))
    dataset_id = db.Column(db.Integer, db.ForeignKey("dataset.id"))
    intervals_id = db.Column(db.Integer, db.ForeignKey("intervals.id"))

    def __repr__(self):
        """Format print output."""
        return f"<AverageIntervalData {self.name}>"

    def to_json(self):
        """Formats json output."""
        json_averageIntervalData = {
            "id": self.id,
            "binsize": self.binsize,
            "name": self.name,
            "file_path": self.file_path,
            "dataset_id": self.dataset_id,
            "intervals_id": self.intervals_id,
            "value_type": self.value_type,
        }
        return json_averageIntervalData


class IndividualIntervalData(db.Model):
    """Table to hold information and pointers to data for
    values extracted at each instance held in the linked intervals dataset.
    E.g. for bigwig stack-ups or displaying snipped Hi-C matrices."""

    id = db.Column(db.Integer, primary_key=True)
    binsize = db.Column(db.Integer)
    name = db.Column(db.String(64), index=True)
    file_path = db.Column(db.String(128), index=True)
    file_path_small = db.Column(
        db.String(128), index=True
    )  # location of downsampled file
    dataset_id = db.Column(
        db.Integer, db.ForeignKey("dataset.id")
    )  # dataset, which was used for value extraction
    intervals_id = db.Column(
        db.Integer, db.ForeignKey("intervals.id")
    )  # intervals over which the values were extracted

    def __repr__(self):
        """Format print output."""
        return f"<IndividualIntervalData {self.name}>"

    def to_json(self):
        """Formats json output."""
        json_individualIntervalData = {
            "id": self.id,
            "binsize": self.binsize,
            "name": self.name,
            "file_path": self.file_path,
            "dataset_id": self.dataset_id,
            "intervals_id": self.intervals_id,
        }
        return json_individualIntervalData


class Task(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    dataset_id = db.Column(db.Integer, db.ForeignKey("dataset.id"))
    complete = db.Column(db.Boolean, default=False)

    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get("progress", 0) if job is not None else 100


class BedFileMetadata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    file_path = db.Column(db.String(128))
    metadata_fields = db.Column(db.String(1024))
    dataset_id = db.Column(
        db.Integer, db.ForeignKey("dataset.id")
    )  # intervals over which the values were extracted

    def __repr__(self):
        """Format print output."""
        return f"<Metadata {self.name}>"



session_dataset_assoc_table = db.Table('session_dataset_assoc_table',
    db.Column('session_id', db.Integer, db.ForeignKey('session.id')),
    db.Column('dataset_id', db.Integer, db.ForeignKey('dataset.id'))
)

class Session(db.Model):
    """Model for session data that represents configurations
    of views. For example, compare views."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    session_object = db.Column(db.String(10**4))
    created_utc = db.Column(db.DateTime, nullable=False,
        default=datetime.datetime.utcnow)
    session_type = db.Column(db.String(100))
    datasets = db.relationship("Dataset",
                               secondary=session_dataset_assoc_table)

    def generate_session_token(self):
        """generates session token"""
        s = JSONWebSignatureSerializer(current_app.config["SECRET_KEY"])
        return s.dumps({"session_id": self.id}).decode("utf-8")

    @staticmethod
    def verify_auth_token(token):
        s = JSONWebSignatureSerializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
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



# helpers


@login.user_loader
def load_user(id):
    """Helper function to load user."""
    return User.query.get(int(id))


def all_tasks_finished(tasks):
    for task in tasks:
        job = task.get_rq_job()
        if job is None:
            # if job is not in queue anymore, it finished successfully
            continue
        if not job.is_finished:
            return False
    return True


def any_tasks_failed(tasks):
    # check whether any job failed
    for task in tasks:
        if task.get_rq_job() is None:
            # job is not available in rq anymore, finished normally TODO: check in documentation about this
            continue
        else:
            if task.get_rq_job().get_status() == "failed":
                return True
    return False
