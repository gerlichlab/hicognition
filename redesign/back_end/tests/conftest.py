import binascii
import logging
import os
import pytest
import tempfile
import shutil
from app import create_app, db
from werkzeug.security import generate_password_hash

@pytest.fixture()
def app():
    c = TestConfig()
    app = create_app(c)
    yield app
    shutil.rmtree(c.FILEUPLOAD_DIR)
    
@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

@pytest.fixture()
def fill_db(app):
    from app.models import User, File
    users = [
        User(
            id=1,
            username='hubert',
            email='hubert@hubert.at',
            password_hash=generate_password_hash('asdf'),
        ),
        User(
            id=2,
            username='toni',
            email='toni@hubert.at',
            password_hash=generate_password_hash('dev')
        )
    ]
    
    tmpdir = app.config['FILEUPLOAD_DIR']
    shutil.copyfile('tests/resources/f1', os.path.join(tmpdir, 'f1'))
    shutil.copyfile('tests/resources/f2', os.path.join(tmpdir, 'f2'))
    
    files = [
        File(
            id=1,
            path=os.path.join(tmpdir, 'f1'),
            md5="912ec803b2ce49e4a541068d495ab570",
            name='f1'
        ),
        File(
            id=2,
            path=os.path.join(tmpdir, 'f2'),
            md5="d251d46b90bb8ce4401cc20de151c331",
            name='f2'
        ),
    ]
    db.session.add_all(users)
    users[0].files.append(files[0])
    users[0].files.append(files[1])
    users[1].files.append(files[1])
    db.session.commit()

class TestConfig:
    RUN_MODE = "TEST"
    FLASK_DEBUG=1
    FLASK_ENV="testing"
    LOGGING=logging.DEBUG
    SECRET_KEY = 'testkey'
    FILEUPLOAD_DIR=tempfile.mkdtemp()
    SQL_CONNECTOR = f"sqlite:////{FILEUPLOAD_DIR}/test.db"
    TESTING = True