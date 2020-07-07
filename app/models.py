"""Database models for HiCognition."""
from werkzeug.security import generate_password_hash, check_password_hash
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

    def __repr__(self):
        """Format print output."""
        return '<User {}>'.format(self.username)


class Dataset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dataset_name = db.Column(db.String(64), index=True, unique=True)
    file_path = db.Column(db.String(128), index=True, unique=True)
    higlass_uuid = db.Column(db.String(64), index=True, unique=True)
    filetype = db.Column(db.String(64), index=True)

    def __repr__(self):
        """Format print output."""
        return f'<Dataset {self.dataset_name}>'


@login.user_loader
def load_user(id):
    """Helper function to load user."""
    return User.query.get(int(id))
