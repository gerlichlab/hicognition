"""Helper functions and classes for unittesting"""
import unittest
import os
import shutil
from base64 import b64encode
from app import create_app, db
from app.models import User



class TempDirTestCase(unittest.TestCase):
    """Will create a temporary directory in the current working 
    directory once before all tests are run that is available via 
    self.tempdir. Removes the directory and all content after
    all tests have been run."""

    @classmethod
    def setUpClass(cls):
        """make test directory."""
        os.mkdir("./tmp_test")
        cls.tempdir = "./tmp_test"

    @classmethod
    def tearDownClass(cls):
        """remove test directory"""
        shutil.rmtree("./tmp_test")


class LoginTest(unittest.TestCase):
    """Testcase that implements generating headers
    for HTTPBasicAuth and creating a flask app."""
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    def get_api_headers(self, username, password):
        return {
            "Authorization": "Basic "
            + b64encode((username + ":" + password).encode("utf-8")).decode("utf-8"),
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def get_token_header(self, token):
        return {
            "Authorization": "Basic "
            + b64encode((token + ":").encode("utf-8")).decode("utf-8"),
            "Accept": "application/json",
            "Content-Type": "application/json",
        }