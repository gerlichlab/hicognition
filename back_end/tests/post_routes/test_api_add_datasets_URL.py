"""Module with tests realted adding datasets."""
import unittest
from unittest.mock import patch

# add path to import app
# import sys
# sys.path.append("./")
from app.models import (
    Dataset,
    Assembly,
    DataRepository,
)
from app import db, create_app
from hicognition.test_helpers import LoginTestCase, TempDirTestCase


class TestAddDataSetsURL(LoginTestCase, TempDirTestCase):
    """Tests route that adds Datasets using URL.
    Form validation tested extensively in test_api_add_datasets
    This tests:
    - rejecting of invalid URL
    - rejecting of invalid forms using files
    - sucess of valid URL
    """

    def setUp(self):
        super().setUp()
        # add assembly
        self.hg19 = Assembly(
            id=1,
            name="hg19",
            chrom_sizes=self.app.config["CHROM_SIZES"],
            chrom_arms=self.app.config["CHROM_ARMS"],
        )

        self.data_repo = DataRepository(
            name="testrepo", url="https://{id}", auth_required=False
        )
        db.session.add(self.hg19)
        db.session.add(self.data_repo)
        db.session.commit()

        self.token_headers = self.get_token_header(
            self.add_and_authenticate("test", "asdf")
        )
        self.token_headers["Content-Type"] = "multipart/form-data"

        self.default_data = {  # TODO there is a better way
            "dataset_name": "test",
            "description": "test-description",
            "assembly": "1",
            "cellCycleStage": "asynchronous",
            "perturbation": "No perturbation",
            "ValueType": "Peak",
            "Method": "ChipSeq",
            "SizeType": "Point",
            "filetype": "bedfile",
            "directionality": "+",
            "public": "false",
            "source_url": "https://thisisavalidbutnotexistingurl.at/file.bed.gz",
        }

    def test_reject_non_url(self):
        """Test that invalid URLs are rejected"""
        data = self.default_data
        fake_urls = ["", "thisisfile", "https://al ksdfj"]

        for url in fake_urls:
            with self.subTest(url=url):
                data["source_url"] = url
                response = self.client.post(
                    "/api/datasets/URL/",
                    data=data,
                    headers=self.token_headers,
                    content_type="multipart/form-data",
                )
                self.assertEqual(response.status_code, 400)
                self.assertTrue("Form is not valid" in response.get_json()["message"])

    def test_reject_files(self):
        """Test that forms including files are rejected"""
        data = self.default_data
        data["file"] = "23"
        response = self.client.post(
            "/api/datasets/URL/",
            data=data,
            headers=self.token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)
        self.assertTrue("Form is not valid" in response.get_json()["message"])

    @patch("app.models.User.launch_task")
    def test_success(self, mock_launch):
        """Test that a valid form runs through and calls the import function"""
        data = self.default_data
        response = self.client.post(
            "/api/datasets/URL/",
            data=data,
            headers=self.token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue("success" in response.get_json()["message"])
        self.assertEqual(len(Dataset.query.all()), 1)
        self.assertEqual(Dataset.query.get(1).upload_state, "new")
        self.assertTrue(mock_launch.called)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
