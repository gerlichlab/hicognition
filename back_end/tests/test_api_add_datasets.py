import sys
import io
import unittest
from unittest.mock import patch
from test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
sys.path.append("./")
from app.models import Dataset


class TestAddDataSets(LoginTestCase, TempDirTestCase):
    """Tests correct launching of
    pipelines after addition of datasets.
    Inherits both from LoginTest and TempDirTestCase
    to be able to login and make temporary directory"""

    @patch("app.models.User.launch_task")
    def test_dataset_added_correctly_cooler(self, mock_launch):
        """Tests whether a cooler dataset is added
        correctly to the Dataset table following
        a post request."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token_header
        token_headers = self.get_token_header(token)
        # add content-type
        token_headers["Content-Type"] = "multipart/form-data"
        # construct form data
        data = {
            "datasetName": "test",
            "description": "test-description",
            "genotype": "WT",
            "filetype": "cooler",
            "file": (io.BytesIO(b"abcdef"), "test.mcool"),
        }
        # dispatch post request
        response = self.client.post(
            "/api/datasets/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        # check whether dataset has been added to database
        self.assertEqual(len(Dataset.query.all()), 1)
        dataset = Dataset.query.first()
        expected = [
            1,
            "test",
            "test-description",
            "WT",
            "cooler",
            1,
            TempDirTestCase.TEMP_PATH + f"{dataset.id}_test.mcool",
        ]
        actual = [
            dataset.id,
            dataset.dataset_name,
            dataset.description,
            dataset.genotype,
            dataset.filetype,
            dataset.user_id,
            dataset.file_path,
        ]
        self.assertEqual(expected, actual)

    @patch("app.models.User.launch_task")
    def test_dataset_added_correctly_cooler_wo_description_and_genotype(
        self, mock_launch
    ):
        """Tests whether a cooler dataset is added
        correctly to the Dataset table following
        a post request."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token_header
        token_headers = self.get_token_header(token)
        # add content-type
        token_headers["Content-Type"] = "multipart/form-data"
        # construct form data
        data = {
            "datasetName": "test",
            "filetype": "cooler",
            "file": (io.BytesIO(b"abcdef"), "test.mcool"),
        }
        # dispatch post request
        response = self.client.post(
            "/api/datasets/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        # check whether dataset has been added to database
        self.assertEqual(len(Dataset.query.all()), 1)
        dataset = Dataset.query.first()
        expected = [
            1,
            "test",
            "No description provided",
            "No genotype provided",
            "cooler",
            1,
            TempDirTestCase.TEMP_PATH + f"{dataset.id}_test.mcool",
        ]
        actual = [
            dataset.id,
            dataset.dataset_name,
            dataset.description,
            dataset.genotype,
            dataset.filetype,
            dataset.user_id,
            dataset.file_path,
        ]
        self.assertEqual(expected, actual)

    @patch("app.models.User.launch_task")
    def test_dataset_added_correctly_bed(self, mock_launch):
        """Tests whether a bed dataset is added
        correctly to the Dataset table following
        a post request."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token_header
        token_headers = self.get_token_header(token)
        # add content-type
        token_headers["Content-Type"] = "multipart/form-data"
        # construct form data
        data = {
            "datasetName": "test",
            "description": "test-description",
            "genotype": "WT",
            "filetype": "bedfile",
            "file": (io.BytesIO(b"abcdef"), "test.bed"),
        }
        # dispatch post request
        response = self.client.post(
            "/api/datasets/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        # check whether dataset has been added to database
        self.assertEqual(len(Dataset.query.all()), 1)
        dataset = Dataset.query.first()
        expected = [
            1,
            "test",
            "test-description",
            "WT",
            "bedfile",
            1,
            TempDirTestCase.TEMP_PATH + f"{dataset.id}_test.bed",
        ]
        actual = [
            dataset.id,
            dataset.dataset_name,
            dataset.description,
            dataset.genotype,
            dataset.filetype,
            dataset.user_id,
            dataset.file_path,
        ]
        self.assertEqual(expected, actual)

    @patch("app.models.User.launch_task")
    def test_incorrect_filetype_is_rejected(self, mock_launch):
        """Tests whether incorrect filetype is rejected"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token_header
        token_headers = self.get_token_header(token)
        # add content-type
        token_headers["Content-Type"] = "multipart/form-data"
        # construct form data
        data = {
            "datasetName": "test",
            "filetype": "bad",
            "file": (io.BytesIO(b"abcdef"), "test.bed"),
        }
        # dispatch post request
        response = self.client.post(
            "/api/datasets/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    @patch("app.models.User.launch_task")
    def test_bed_pipeline_launched_correctly(self, mock_launch):
        """Tests whether bed pipeline is called with the right arguments."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token_header
        token_headers = self.get_token_header(token)
        # add content-type
        token_headers["Content-Type"] = "multipart/form-data"
        # construct form data
        data = {
            "datasetName": "test",
            "filetype": "bedfile",
            "file": (io.BytesIO(b"abcdef"), "test.bed"),
        }
        # dispatch post request
        response = self.client.post(
            "/api/datasets/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        # check whether launch task has been called with the right arguments
        mock_launch.assert_called_with("pipeline_bed", "run bed preprocessing", 1)

    def test_badform_no_datasetName(self):
        """Tests whether form without datasetName is rejected"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token_header
        token_headers = self.get_token_header(token)
        # add content-type
        token_headers["Content-Type"] = "multipart/form-data"
        # construct form data
        data = {
            "filetype": "bedfile",
            "file": (io.BytesIO(b"abcdef"), "test.bed"),
        }
        # dispatch post request
        response = self.client.post(
            "/api/datasets/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    def test_badform_no_fileObject(self):
        """Tests whether form without file is rejected"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token_header
        token_headers = self.get_token_header(token)
        # add content-type
        token_headers["Content-Type"] = "multipart/form-data"
        # construct form data
        data = {"datasetName": "test", "filetype": "bedfile"}
        # dispatch post request
        response = self.client.post(
            "/api/datasets/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    def test_badform_bed_file_cooler_filetype(self):
        """Tests whether form with bedfile, but cooler file-ending is rejected"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token_header
        token_headers = self.get_token_header(token)
        # add content-type
        token_headers["Content-Type"] = "multipart/form-data"
        # construct form data
        data = {
            "datasetName": "test",
            "filetype": "bedfile",
            "file": (io.BytesIO(b"abcdef"), "test.mcool"),
        }
        # dispatch post request
        response = self.client.post(
            "/api/datasets/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    def test_badform_cooler_file_bed_filetype(self):
        """Tests whether form with cooler, but bed file-ending is rejected"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token_header
        token_headers = self.get_token_header(token)
        # add content-type
        token_headers["Content-Type"] = "multipart/form-data"
        # construct form data
        data = {
            "datasetName": "test",
            "filetype": "cooler",
            "file": (io.BytesIO(b"abcdef"), "test.bed"),
        }
        # dispatch post request
        response = self.client.post(
            "/api/datasets/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    def test_badform_not_fileending_rejected(self):
        """Tests whether form with file without ending is rejected."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token_header
        token_headers = self.get_token_header(token)
        # add content-type
        token_headers["Content-Type"] = "multipart/form-data"
        # construct form data
        data = {
            "datasetName": "test",
            "filetype": "cooler",
            "file": (io.BytesIO(b"abcdef"), "test"),
        }
        # dispatch post request
        response = self.client.post(
            "/api/datasets/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    def test_public_flag_set_correctly_if_true(self):
        """Tests whether form with file without ending is rejected."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token_header
        token_headers = self.get_token_header(token)
        # add content-type
        token_headers["Content-Type"] = "multipart/form-data"
        # construct form data
        data = {
            "datasetName": "test",
            "filetype": "bedfile",
            "public": "True",
            "file": (io.BytesIO(b"abcdef"), "test.bed"),
        }
        # dispatch post request
        response = self.client.post(
            "/api/datasets/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        # check if public flag is set correctly
        dataset = Dataset.query.get(1)
        self.assertTrue(dataset.public)

    def test_public_flag_set_correctly_if_false(self):
        """Tests whether form with file without ending is rejected."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token_header
        token_headers = self.get_token_header(token)
        # add content-type
        token_headers["Content-Type"] = "multipart/form-data"
        # construct form data
        data = {
            "datasetName": "test",
            "filetype": "bedfile",
            "public": "False",
            "file": (io.BytesIO(b"abcdef"), "test.bed"),
        }
        # dispatch post request
        response = self.client.post(
            "/api/datasets/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        # check if public flag is set correctly
        dataset = Dataset.query.get(1)
        self.assertFalse(dataset.public)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
