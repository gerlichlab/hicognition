"""Database models for HiCognition."""
from flask.globals import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin
from app import db, login


class User(db.Model, UserMixin):
    """User database model"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

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
    dataset_name = db.Column(db.String(64), index=True, unique=True)
    file_path = db.Column(db.String(128), index=True, unique=True)
    higlass_uuid = db.Column(db.String(64), index=True, unique=True)
    filetype = db.Column(db.String(64), index=True)
    pileup_regions = db.relationship("Pileupregion", backref="source_dataset", lazy="dynamic")
    pileup = db.relationship("Pileup", backref="source_cooler", lazy="dynamic")

    def __repr__(self):
        """Format print output."""
        return f'<Dataset {self.dataset_name}>'


class Pileupregion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey("dataset.id"))
    name = db.Column(db.String(64), index=True, unique=True)
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
    name = db.Column(db.String(64), index=True, unique=True)
    file_path = db.Column(db.String(128), index=True)
    cooler_id = db.Column(db.Integer, db.ForeignKey("dataset.id"))
    pileupregion_id = db.Column(db.Integer, db.ForeignKey("pileupregion.id"))

    def __repr__(self):
        """Format print output."""
        return f"<Pileup {self.name}>"

@login.user_loader
def load_user(id):
    """Helper function to load user."""
    return User.query.get(int(id))
