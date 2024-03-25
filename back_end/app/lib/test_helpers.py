"""Helper functions and classes for unittesting"""
import logging
import unittest
import os
import shutil
from base64 import b64encode

# add path to import app
import sys

sys.path.append("./")
from app import create_app, db
from app.models import User, Organism, Dataset, Assembly


class TempDirTestCase(unittest.TestCase):
    """Will create a temporary directory in the current working
    directory once before all tests are run that is available via
    self.tempdir. Removes the directory and all content after
    all tests have been run."""

    TEMP_PATH = "./tmp_test/"

    @classmethod
    def setUpClass(cls):
        """make test directory."""
        if os.path.exists(cls.TEMP_PATH):
            logging.warning("Had to remove temp directory")
            shutil.rmtree(cls.TEMP_PATH)
        os.mkdir(cls.TEMP_PATH)

    @classmethod
    def tearDownClass(cls):
        """remove test directory"""
        shutil.rmtree(cls.TEMP_PATH)


class LoginTestCase(unittest.TestCase):
    """Testcase that implements generating headers
    for HTTPBasicAuth and creating a flask app."""

    def setUp(self):
        self.dataset_id_index = 1
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def create_dataset(
        self,
        add_and_commit: bool = False,
        user_id: int = None,
        assembly_id: int = None,
        id: int = None,
        **key_value_pairs: dict
    ) -> Dataset:
        dataset = self.create_default_dataset(user_id, assembly_id, id=id)
        # fill with data
        [dataset.__setattr__(key, value) for key, value in key_value_pairs.items()]

        if add_and_commit:
            db.session.add(dataset)
            db.session.commit()

        return dataset

    def create_default_dataset(
        self, user_id: int = None, assembly: int = None, id: int = None
    ) -> Dataset:
        if id is None:
            id = self.dataset_id_index
            self.dataset_id_index += 1

        return Dataset(
            id=id,
            user_id=user_id,
            assembly=assembly,
            dataset_name="test",
            filetype="bedfile",
            public=False,
            upload_state="new",
            processing_state="new",
        )

    def add_default_assembly(self, add_and_commit: bool = False):
        self.hg19 = Assembly(
            id=1,
            name="hg19",
            chrom_sizes=self.app.config["CHROM_SIZES"],
            chrom_arms=self.app.config["CHROM_ARMS"],
        )
        if add_and_commit:
            db.session.add(self.hg19)
            db.session.commit()

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

    def add_and_authenticate(self, username, password):
        """adds a user with username and password, authenticates
        the user and returns a token."""
        # add new user
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        # get token
        headers = self.get_api_headers(username, password)
        response = self.client.post(
            "/api/tokens/", headers=headers, content_type="application/json"
        )
        return response.get_json()["token"]
