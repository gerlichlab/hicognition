"""Database models for HiCognition."""
from flask.globals import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
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
    tasks = db.relationship('Task', backref='user', lazy='dynamic')

    def set_password(self, password):
        """set password helper."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """check password helper."""
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expiration):
        """generates authentication token"""
        s = Serializer(current_app.config["SECRET_KEY"],
                       expires_in=expiration)
        return s.dumps({"id": self.id}).decode("utf-8")

    def launch_task(self, name, description, dataset_id, *args, **kwargs):
        rq_job = current_app.task_queue.enqueue('app.tasks.' + name, dataset_id,
                                                job_timeout="10h",
                                                *args, **kwargs)
        task = Task(id=rq_job.get_id(), name=name, description=description,
                    user_id=self.id, dataset_id=dataset_id)
        db.session.add(task)
        return task

    def get_tasks_in_progress(self):
        return Task.query.filter_by(user=self, complete=False).all()

    def get_task_in_progress(self, name):
        return Task.query.filter_by(name=name, user=self,
                                    complete=False).first()

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
        return '<User {}>'.format(self.username)


class Dataset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dataset_name = db.Column(db.String(64), index=True)
    file_path = db.Column(db.String(128), index=True)
    higlass_uuid = db.Column(db.String(64), index=True, unique=True)
    filetype = db.Column(db.String(64), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    pileup_regions = db.relationship("Pileupregion", backref="source_dataset", lazy="dynamic")
    pileup = db.relationship("Pileup", backref="source_cooler", lazy="dynamic")
    tasks = db.relationship('Task', backref='dataset', lazy='dynamic')

    def get_tasks_in_progress(self):
        return Task.query.filter_by(dataset=self, complete=False).all()

    def __repr__(self):
        """Format print output."""
        return f'<Dataset {self.dataset_name}>'

    def to_json(self):
        # check whether there are any uncompleted of failed tasks
        tasks = self.tasks.filter(Task.complete == False).all()
        if len(tasks) == 0:
            completed = 1
        else:
            completed = 0
            # check whether any job failed
            for task in tasks:
                if task.get_rq_job() is None:
                    # job is not available in rq anymore, finished normally TODO: check in documentation about this
                    continue
                else:
                    if task.get_rq_job().get_status() == "failed":
                        completed = - 1
        json_dataset = {
            "id": self.id,
            "dataset_name": self.dataset_name,
            "file_path": self.file_path,
            "higlass_uuid": self.higlass_uuid,
            "filetype": self.filetype,
            "user_id": self.user_id,
            "completed": completed
        }
        return json_dataset


class Pileupregion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey("dataset.id"))
    name = db.Column(db.String(64), index=True)
    file_path = db.Column(db.String(128), index=True)
    higlass_uuid = db.Column(db.String(64), index=True)
    windowsize = db.Column(db.Integer, index=True)
    pileups = db.relationship("Pileup", backref="source_pileupregion", lazy="dynamic")

    def __repr__(self):
        """Format print output."""
        return f'<Pileupregion {self.name}>'


class Pileup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    binsize = db.Column(db.Integer)
    name = db.Column(db.String(64), index=True)
    file_path = db.Column(db.String(128), index=True)
    cooler_id = db.Column(db.Integer, db.ForeignKey("dataset.id"))
    pileupregion_id = db.Column(db.Integer, db.ForeignKey("pileupregion.id"))

    def __repr__(self):
        """Format print output."""
        return f"<Pileup {self.name}>"


class Task(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.id'))
    complete = db.Column(db.Boolean, default=False)

    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get('progress', 0) if job is not None else 100

# helpers

@login.user_loader
def load_user(id):
    """Helper function to load user."""
    return User.query.get(int(id))