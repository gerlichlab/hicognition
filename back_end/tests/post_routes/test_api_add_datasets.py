"""Module with tests realted adding datasets."""
import os
import io
import unittest
from unittest.mock import patch
from unittest import mock
from tests.test_utils.test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
# import sys
# sys.path.append("./")
from app.models import Dataset, Assembly
from app import db


class TestAddDataSets(LoginTestCase, TempDirTestCase):
    """Tests correct launching of
    pipelines after addition of datasets.
    Inherits both from LoginTest and TempDirTestCase
    to be able to login and make temporary directory"""

    maxDiff = None

    def setUp(self):
        super().setUp()
        # add assembly
        self.hg19 = Assembly(
            id=1,
            name="hg19",
            chrom_sizes=self.app.config["CHROM_SIZES"],
            chrom_arms=self.app.config["CHROM_ARMS"],
        )
        db.session.add(self.hg19)
        db.session.commit()
        # add token headers
        token = self.add_and_authenticate("test", "asdf")
        # create token_header
        self.token_headers = self.get_token_header(token)
        # add content-type
        self.token_headers["Content-Type"] = "multipart/form-data"

    @patch("app.models.User.launch_task")
    def test_dataset_added_correctly_cooler(self, mock_launch):
        """Tests whether a cooler dataset is added
        correctly to the Dataset table following
        a post request."""
        # construct form data
        data = {
            "dataset_name": "test",
            "description": "test-description",
            "assembly": "1",
            "cell_type": "undefined",
            "perturbation": "No perturbation",
            "filetype": "cooler",
            "public": "false",
            "file": (open("tests/testfiles/test.mcool", "rb"), "test.mcool"),
        }
        # dispatch post request
        response = self.client.post(
            "/api/datasets/",
            data=data,
            headers=self.token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        # check whether dataset has been added to database
        self.assertEqual(len(Dataset.query.all()), 1)
        dataset = Dataset.query.first()
        expected = {
            "dataset_name": "test",
            "dimension": "1d",
            "processing_state": "new",
            "upload_state": "uploaded",
            "description": "test-description",
            "perturbation": "No perturbation",
            "cell_type": 'undefined',
            "file_path": "./tmp_test/1_test.mcool",
            "assembly": 1,
            "public": False,
            "processing_datasets": [],
            "failed_datasets": [],
            "processing_collections": [],
            "failed_collections": [],
            "filetype": "cooler",
            "user_id": 1,
            "id": 1,
            "sizeType": "undefined",
            "repository_name": None,
            "sample_id": None,
            "source_url": None,
        }
        self.assertEqual(expected, dataset.to_json())
        # test whether uploaded file exists
        self.assertTrue(os.path.exists(dataset.file_path))
        # test whether uploaded file is equal to expected file
        expected_file = open("tests/testfiles/test.mcool", "rb").read()
        actual_file = open(dataset.file_path, "rb").read()
        self.assertEqual(expected_file, actual_file)

    @patch("app.models.User.launch_task")
    def test_dataset_added_correctly_bigwig_bw_ending(self, mock_launch):
        """Tests whether a bigwig dataset is added
        correctly to the Dataset table following
        a post request."""
        # construct form data
        data = {
            "dataset_name": "test",
            "assembly": "1",
            "cell_type": 'undefined',
            "perturbation": "No perturbation",
            "description": "test-description",
            "public": "false",
            "filetype": "bigwig",
            "file": (open("tests/testfiles/test.bw", "rb"), "test.bw"),
        }
        # dispatch post request
        response = self.client.post(
            "/api/datasets/",
            data=data,
            headers=self.token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        # check whether dataset has been added to database
        self.assertEqual(len(Dataset.query.all()), 1)
        dataset = Dataset.query.first()
        expected = {
            "id": 1,
            "user_id": 1,
            "dataset_name": "test",
            "dimension": "1d",
            "processing_state": "new",
            "upload_state": "uploaded",
            "description": "test-description",
            "perturbation": "No perturbation",
            "cell_type": 'undefined',
            "file_path": "./tmp_test/1_test.bw",
            "processing_datasets": [],
            "failed_datasets": [],
            "processing_collections": [],
            "failed_collections": [],
            "assembly": 1,
            "public": False,
            "filetype": "bigwig",
            "sizeType": "undefined",
            "repository_name": None,
            "sample_id": None,
            "source_url": None,
        }
        self.assertEqual(expected, dataset.to_json())
        # test whether uploaded file exists
        self.assertTrue(os.path.exists(dataset.file_path))
        # test whether uploaded file is equal to expected file
        with open("tests/testfiles/test.bw", "rb") as expected_file, open(
            dataset.file_path, "rb"
        ) as actual_file:
            self.assertEqual(expected_file.read(), actual_file.read())

    @patch("app.models.User.launch_task")
    def test_dataset_added_correctly_bigwig_bigwig_ending(self, mock_launch):
        """Tests whether a bigwig dataset is added
        correctly to the Dataset table following
        a post request."""
        # construct form data
        data = {
            "dataset_name": "test",
            "assembly": "1",
            "perturbation": "No perturbation",
            "description": "test-description",
            "cell_type": 'undefined',
            "public": "false",
            "filetype": "bigwig",
            "file": (open("tests/testfiles/test.bigwig", "rb"), "test.bigwig"),
        }
        # dispatch post request
        response = self.client.post(
            "/api/datasets/",
            data=data,
            headers=self.token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        # check whether dataset has been added to database
        self.assertEqual(len(Dataset.query.all()), 1)
        dataset = Dataset.query.first()
        expected = {
            "id": 1,
            "user_id": 1,
            "dataset_name": "test",
            "dimension": "1d",
            "description": "test-description",
            "perturbation": "No perturbation",
            "file_path": "./tmp_test/1_test.bigwig",
            "cell_type": 'undefined',
            "upload_state": "uploaded",
            "processing_state": "new",
            "processing_datasets": [],
            "failed_datasets": [],
            "processing_collections": [],
            "failed_collections": [],
            "sizeType": "undefined",
            "assembly": 1,
            "public": False,
            "filetype": "bigwig",
            "repository_name": None,
            "sample_id": None,
            "source_url": None,
        }
        self.assertEqual(expected, dataset.to_json())
        # test whether uploaded file exists
        self.assertTrue(os.path.exists(dataset.file_path))
        # test whether uploaded file is equal to expected file
        with open("tests/testfiles/test.bw", "rb") as expected_file, open(
            dataset.file_path, "rb"
        ) as actual_file:
            self.assertEqual(expected_file.read(), actual_file.read())

    @patch("app.models.User.launch_task")
    def test_dataset_added_correctly_cooler_wo_description(
        self, mock_launch
    ):
        """Tests whether a cooler dataset is added
        correctly to the Dataset table following
        a post request."""
        # construct form data
        data = {
            "dataset_name": "test",
            "assembly": "1",
            "cell_type": "undefined",
            "perturbation": "No perturbation",
            "filetype": "cooler",
            "public": "false",
            "file": (open("tests/testfiles/test.mcool", "rb"), "test.mcool"),
        }
        # dispatch post request
        response = self.client.post(
            "/api/datasets/",
            data=data,
            headers=self.token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        # check whether dataset has been added to database
        self.assertEqual(len(Dataset.query.all()), 1)
        dataset = Dataset.query.first()
        expected = {
            "dataset_name": "test",
            "processing_state": "new",
            "upload_state": "uploaded",
            "dimension": "1d",
            "description": "No description provided",
            "perturbation": "No perturbation",
            "cell_type": 'undefined',
            "file_path": "./tmp_test/1_test.mcool",
            "assembly": 1,
            "public": False,
            "processing_datasets": [],
            "failed_datasets": [],
            "processing_collections": [],
            "failed_collections": [],
            "filetype": "cooler",
            "user_id": 1,
            "id": 1,
            "sizeType": "undefined",
            "repository_name": None,
            "sample_id": None,
            "source_url": None,
        }
        self.assertEqual(expected, dataset.to_json())

    @patch("app.models.User.launch_task")
    def test_dataset_added_correctly_bed(self, mock_launch):
        """Tests whether a bed dataset is added
        correctly to the Dataset table following
        a post request."""
        # construct form data
        data = {
            "dataset_name": "test",
            "assembly": "1",
            "description": "test-description",
            "perturbation": "No perturbation",
            "cell_type": "undefined",
            "public": "false",
            "SizeType": "interval",
            "filetype": "bedfile",
            "file": (open("tests/testfiles/tad_boundaries.bed", "rb"), "test.bed"),
        }
        # dispatch post request
        response = self.client.post(
            "/api/datasets/",
            data=data,
            headers=self.token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        # check whether dataset has been added to database
        self.assertEqual(len(Dataset.query.all()), 1)
        dataset = Dataset.query.first()
        expected = {
            "dataset_name": "test",
            "dimension": "1d",
            "processing_state": "processing",
            "cell_type": 'undefined',
            "upload_state": "uploaded",
            "description": "test-description",
            "sizeType": "interval",
            "perturbation": "No perturbation",
            "file_path": "./tmp_test/1_test.bed",
            "processing_datasets": [],
            "failed_datasets": [],
            "processing_collections": [],
            "failed_collections": [],
            "assembly": 1,
            "public": False,
            "user_id": 1,
            "filetype": "bedfile",
            "id": 1,
            "repository_name": None,
            "sample_id": None,
            "source_url": None,
        }
        self.assertEqual(expected, dataset.to_json())
        # test whether uploaded file exists
        self.assertTrue(os.path.exists(dataset.file_path))
        # test whether uploaded file is equal to expected file
        with open(dataset.file_path, "rb") as actual_file, open("tests/testfiles/tad_boundaries.bed", "rb") as expected_file:
            self.assertEqual(expected_file.read(), actual_file.read())

    @patch("app.models.User.launch_task")
    def test_dataset_added_correctly_bedpe(self, mock_launch):
        """Tests whether a bedpe dataset is added
        correctly to the Dataset table following
        a post request."""
        # construct form data
        data = {
            "dataset_name": "test",
            "assembly": "1",
            "description": "test-description",
            "perturbation": "No perturbation",
            "cell_type": "undefined",
            "public": "false",
            "SizeType": "interval",
            "filetype": "bedfile",
            "file": (open("tests/testfiles/test_small.bedpe", "rb"), "test_small.bedpe"),
        }
        # dispatch post request
        response = self.client.post(
            "/api/datasets/",
            data=data,
            headers=self.token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        # check whether dataset has been added to database
        self.assertEqual(len(Dataset.query.all()), 1)
        dataset = Dataset.query.first()
        expected = {
            "dataset_name": "test",
            "processing_state": "processing",
            "upload_state": "uploaded",
            "dimension": "2d",
            "description": "test-description",
            "sizeType": "interval",
            "cell_type": "undefined",
            "perturbation": "No perturbation",
            "file_path": "./tmp_test/1_test_small.bedpe",
            "processing_datasets": [],
            "failed_datasets": [],
            "processing_collections": [],
            "failed_collections": [],
            "assembly": 1,
            "public": False,
            "filetype": "bedfile",
            "user_id": 1,
            "id": 1,
            "repository_name": None,
            "sample_id": None,
            "source_url": None,
        }
        self.assertEqual(expected, dataset.to_json())
        # test whether uploaded file exists
        self.assertTrue(os.path.exists(dataset.file_path))
        # test whether uploaded file is equal to expected file
        with open(dataset.file_path, "rb") as actual_file, open("tests/testfiles/test_small.bedpe", "rb") as expected_file:
            self.assertEqual(expected_file.read(), actual_file.read())

    @patch("app.models.User.launch_task")
    def test_incorrect_filetype_is_rejected(self, mock_launch):
        """Tests whether incorrect filetype is rejected"""
        # construct form data
        data = {
            "dataset_name": "test",
            "assembly": "1",
            "description": "test-description",
            "cell_type": "undefined",
            "perturbation": "undefined",
            "public": "false",
            "SizeType": "interval",
            "filetype": "bad",
            "file": (io.BytesIO(b"abcdef"), "test.bed"),
        }
        # dispatch post request
        response = self.client.post(
            "/api/datasets/",
            data=data,
            headers=self.token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)
        
    @patch("app.models.Dataset.validate_dataset")
    @patch("app.models.User.launch_task")
    def test_bed_pipeline_launched_correctly(self, mock_launch, mock_prepr):
        """Tests whether bed pipeline is called with the right arguments."""
        # construct form data
        data = {
            "dataset_name": "test",
            "assembly": "1",
            "description": "test-description",
            "perturbation": "No perturbation",
            "cell_type": "undefined",
            "public": "false",
            "SizeType": "interval",
            "filetype": "bedfile",
            "file": (open("tests/testfiles/tad_boundaries.bed", "rb"), "test.bed"),
        }
        # dispatch post request
        response = self.client.post(
            "/api/datasets/",
            data=data,
            headers=self.token_headers,
            content_type="multipart/form-data",
        )
        # # check whether launch task has been called with the right arguments
        # mock_launch.assert_called_with(
        #     self.app.queues["short"], "pipeline_bed", "run bed preprocessing", 1
        # )
        # check whether launch task has been called with the right arguments
        import app.tasks
        mock_launch.assert_called_with(
            self.app.queues["short"], app.tasks.pipeline_bed, "run bed preprocessing", 1
        )

    def test_badform_no_dataset_name(self):
        """Tests whether form without datasetName is rejected"""
        # construct form data
        data = {
            "assembly": "1",
            "description": "test-description",
            "cell_type": "undefined",
            "perturbation": "undefined",
            "public": "false",
            "SizeType": "interval",
            "filetype": "bad",
            "file": (io.BytesIO(b"abcdef"), "test.bed"),
        }
        # dispatch post request
        response = self.client.post(
            "/api/datasets/",
            data=data,
            headers=self.token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    def test_badform_no_file_object(self):
        """Tests whether form without file is rejected"""
        # construct form data
        data = {
            "dataset_name": "test",
            "assembly": "1",
            "description": "test-description",
            "cell_type": "undefined",
            "perturbation": "undefined",
            "public": "false",
            "SizeType": "interval",
            "filetype": "bedfile",
        }
        # dispatch post request
        response = self.client.post(
            "/api/datasets/",
            data=data,
            headers=self.token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    def test_badform_bed_file_cooler_filetype(self):
        """Tests whether form with bedfile, but cooler file-ending is rejected"""
        # construct form data
        data = {
            "dataset_name": "test",
            "assembly": "1",
            "description": "test-description",
            "cell_type": "undefined",
            "perturbation": "undefined",
            "public": "false",
            "SizeType": "interval",
            "filetype": "bedfile",
            "file": (io.BytesIO(b"abcdef"), "test.mcool"),
        }
        # dispatch post request
        response = self.client.post(
            "/api/datasets/",
            data=data,
            headers=self.token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    def test_badform_cooler_file_bed_filetype(self):
        """Tests whether form with cooler, but bed file-ending is rejected"""
        # construct form data
        data = {
            "dataset_name": "test",
            "assembly": "1",
            "description": "test-description",
            "cell_type": "undefined",
            "perturbation": "undefined",
            "public": "false",
            "SizeType": "interval",
            "filetype": "cooler",
            "file": (io.BytesIO(b"abcdef"), "test.bed"),
        }
        # dispatch post request
        response = self.client.post(
            "/api/datasets/",
            data=data,
            headers=self.token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    def test_badform_no_fileending_rejected(self):
        """Tests whether form with file without ending is rejected."""
        # construct form data
        data = {
            "dataset_name": "test",
            "assembly": "1",
            "description": "test-description",
            "cell_type": "undefined",
            "perturbation": "undefined",
            "public": "false",
            "SizeType": "interval",
            "filetype": "bedfile",
            "file": (io.BytesIO(b"abcdef"), "test"),
        }
        # dispatch post request
        response = self.client.post(
            "/api/datasets/",
            data=data,
            headers=self.token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    def test_wrongly_formatted_bedfile_rejected(self):
        """Tests whether form with wrongly formatted bedfile is rejected."""
        # construct form data
        data = {
            "dataset_name": "test",
            "assembly": "1",
            "description": "test-description",
            "cell_type": "undefined",
            "perturbation": "undefined",
            "public": "false",
            "SizeType": "interval",
            "filetype": "bedfile",
            "file": open("tests/testfiles/wrongly_formatted_bedfile.bed", "rb"),
        }
        # dispatch post request
        response = self.client.post(
            "/api/datasets/",
            data=data,
            headers=self.token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)
        # check whether database entry was removed
        self.assertEqual(0, len(Dataset.query.all()))
        # test whether file was removed, filename will bed 1_wrongly_formatted_bedfile.bed
        self.assertFalse(
            os.path.exists(
                os.path.join(
                    TempDirTestCase.TEMP_PATH, "1_wrongly_formatted_bedfile.bed"
                )
            )
        )

    def test_wrongly_formatted_coolerfile_rejected(self):
        """Tests whether form with wrongly formatted/corrupted coolerfile is
        rejected."""
        # construct form data
        data = {
            "dataset_name": "test",
            "assembly": "1",
            "description": "test-description",
            "cell_type": "undefined",
            "perturbation": "undefined",
            "public": "false",
            "SizeType": "interval",
            "filetype": "cooler",
            "file": (open("tests/testfiles/bad_cooler.mcool", "rb"), "test.mcool"),
        }
        # dispatch post request
        response = self.client.post(
            "/api/datasets/",
            data=data,
            headers=self.token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)
        # check whether database entry was removed
        self.assertEqual(0, len(Dataset.query.all()))
        # test whether file was removed, filename will bed 1_bad_cooler.mcool
        self.assertFalse(
            os.path.exists(
                os.path.join(TempDirTestCase.TEMP_PATH, "1_bad_cooler.mcool")
            )
        )

    @patch("app.models.Dataset.validate_dataset")
    @patch("app.models.Dataset.preprocess_dataset")
    @patch("app.models.User.launch_task")
    def test_public_flag_set_correctly_if_true(self, mock_launch_task, mock_prep, mock_validate):
        """Tests whether form with file without ending is rejected."""
        # mock config
        self.app.config.update({'ALLOW_PUBLIC_UPLOAD': True})
        # construct form data
        data = {
            "dataset_name": "test",
            "assembly": "1",
            "description": "test-description",
            "cell_type": "undefined",
            "perturbation": "undefined",
            "public": "true",
            "SizeType": "interval",
            "filetype": "bedfile",
            "file": (io.BytesIO(b"abcdef"), "test.bed"),
        }
        # dispatch post request
        response = self.client.post(
            "/api/datasets/",
            data=data,
            headers=self.token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        # check if public flag is set correctly
        dataset = Dataset.query.get(1)
        self.assertTrue(dataset.public)

    @patch("app.models.Dataset.validate_dataset")
    @patch("app.models.Dataset.preprocess_dataset")
    @patch("app.models.User.launch_task")
    def test_public_dataset_denied_if_not_allowed(self, mock_launch_task, mock_prep, mock_validate):
        """Tests whether form with file without ending is rejected."""
        # mock config
        self.app.config.update({'ALLOW_PUBLIC_UPLOAD': False})
        # construct form data
        data = {
            "dataset_name": "test",
            "assembly": "1",
            "description": "test-description",
            "cell_type": "undefined",
            "perturbation": "undefined",
            "public": "true",
            "SizeType": "interval",
            "filetype": "bedfile",
            "file": (io.BytesIO(b"abcdef"), "test.bed"),
        }
        # dispatch post request
        response = self.client.post(
            "/api/datasets/",
            data=data,
            headers=self.token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    @patch("app.models.Dataset.validate_dataset")
    @patch("app.models.Dataset.preprocess_dataset")
    @patch("app.models.User.launch_task")
    def test_public_flag_set_correctly_if_false(self, mock_launch_task, mock_preprocess, mock_validate):
        """Tests whether form with file without ending is rejected."""
        # construct form data
        data = {
            "dataset_name": "test",
            "assembly": "1",
            "description": "test-description",
            "cell_type": "undefined",
            "perturbation": "undefined",
            "public": "false",
            "SizeType": "interval",
            "filetype": "bedfile",
            "file": (io.BytesIO(b"abcdef"), "test.bed"),
        }
        # dispatch post request
        response = self.client.post(
            "/api/datasets/",
            data=data,
            headers=self.token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        # check if public flag is set correctly
        dataset = Dataset.query.get(1)
        self.assertFalse(dataset.public)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
