from functools import partial
import sys
import unittest
from unittest.mock import patch
from test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
sys.path.append("./")
from app import db
from app.models import Dataset, Intervals
from app.tasks import pipeline_cooler


class TestPipelineCooler(LoginTestCase, TempDirTestCase):
    """Tests whether pipelin_bed task calls
    the pipeline steps correctly"""

    def setUp(self):
        """Add test dataset"""
        # call setUp of LoginTestCase to initialize app
        super(TestPipelineCooler, self).setUp()
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token_header
        token_headers = self.get_token_header(token)
        # add content-type
        token_headers["Content-Type"] = "multipart/form-data"
        # add dataset
        dataset = Dataset(
            dataset_name="test3",
            file_path="/test/path/test3.mcool",
            higlass_uuid="fdsa8765",
            filetype="cooler",
            processing_state="finished",
            user_id=1,
        )
        db.session.add(dataset)
        db.session.commit()

    @patch("app.tasks.higlass_interface.add_tileset")
    def test_cooler_added_correctly_to_higlass(self, mock_add_tileset):
        """Tests whether the functions that execute the different pipeline steps are called
        correctly."""
        mock_add_tileset.return_value = {"uuid": "higlass_uuid"}
        # launch task
        pipeline_cooler(1)
        # check whether sort_bed was called correctly
        credentials = {
            "user": self.app.config["HIGLASS_USER"],
            "password": self.app.config["HIGLASS_PWD"],
        }
        mock_add_tileset.assert_called_with(
            *[
                "cooler",
                "/test/path/test3.mcool",
                self.app.config["HIGLASS_API"],
                credentials,
                "test3"
            ]
        )
        # check whether uuid is added to database
        check_dataset = Dataset.query.get(1)
        self.assertEqual(check_dataset.higlass_uuid, "higlass_uuid")


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
