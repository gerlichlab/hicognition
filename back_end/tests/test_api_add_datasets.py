import sys
import os
import io
import json
import unittest
from unittest.mock import patch
from test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
sys.path.append("./")
from app.models import Dataset, Assembly
from app import db


class TestAddDataSets(LoginTestCase, TempDirTestCase):
    """Tests correct launching of
    pipelines after addition of datasets.
    Inherits both from LoginTest and TempDirTestCase
    to be able to login and make temporary directory"""

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

    @patch("app.api.post_routes.parse_binsizes")
    @patch("app.models.User.launch_task")
    def test_dataset_added_correctly_cooler(self, mock_launch, mock_parse_binsizes):
        """Tests whether a cooler dataset is added
        correctly to the Dataset table following
        a post request."""
        # define return values
        mock_parse_binsizes.return_value = [5000000]
        # construct form data
        data = {
            "datasetName": "test",
            "description": "test-description",
            "assembly": "1",
            "cellCycleStage": "asynchronous",
            "perturbation": "No perturbation",
            "ValueType": "Interaction",
            "Method": "HiC",
            "Normalization": "ICCF",
            "filetype": "cooler",
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
            "normalization": "ICCF",
            "dataset_name": "test",
            "processing_state": "uploaded",
            "description": "test-description",
            "perturbation": "No perturbation",
            "file_path": "./tmp_test/1_test.mcool",
            "assembly": 1,
            "public": False,
            "processing_datasets": [],
            "failed_datasets": [],
            "processing_collections": [],
            "failed_collections": [],
            "cellCycleStage": "asynchronous",
            "valueType": "Interaction",
            "filetype": "cooler",
            "method": "HiC",
            "available_binsizes": '["5000000"]',
            "user_id": 1,
            "id": 1,
        }
        self.assertEqual(expected, dataset.to_json())
        # test whether uploaded file exists
        self.assertTrue(os.path.exists(dataset.file_path))
        # test whether uploaded file is equal to expected file
        expected_file = open("tests/testfiles/test.mcool", "rb").read()
        actual_file = open(dataset.file_path, "rb").read()
        self.assertEqual(expected_file, actual_file)

    @patch("app.api.post_routes.parse_binsizes")
    @patch("app.models.User.launch_task")
    def test_cooler_w_wrong_binsize_rejected(self, mock_launch, mock_parse_binsizes):
        """Tests whether a cooler dataset lacking needed binsizes is rejected."""
        # define return values
        mock_parse_binsizes.return_value = [1]
        # construct form data
        data = {
            "datasetName": "test",
            "description": "test-description",
            "assembly": "1",
            "cellCycleStage": "asynchronous",
            "perturbation": "No perturbation",
            "ValueType": "Interaction",
            "Method": "HiC",
            "Normalization": "ICCF",
            "filetype": "cooler",
            "file": (open("tests/testfiles/test.mcool", "rb"), "test.mcool"),
        }
        # dispatch post request
        response = self.client.post(
            "/api/datasets/",
            data=data,
            headers=self.token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    @patch("app.models.User.launch_task")
    def test_dataset_added_correctly_bigwig_bw_ending(self, mock_launch):
        """Tests whether a bigwig dataset is added
        correctly to the Dataset table following
        a post request."""
        # construct form data
        data = {
            "datasetName": "test",
            "assembly": "1",
            "cellCycleStage": "asynchronous",
            "perturbation": "No perturbation",
            "description": "test-description",
            "ValueType": "ChromatinAssociation",
            "Protein": "CTCF",
            "Method": "ChipSeq",
            "Normalization": "RPM",
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
            "method": "ChipSeq",
            "id": 1,
            "user_id": 1,
            "normalization": "RPM",
            "dataset_name": "test",
            "processing_state": "uploaded",
            "description": "test-description",
            "perturbation": "No perturbation",
            "file_path": "./tmp_test/1_test.bw",
            "processing_datasets": [],
            "failed_datasets": [],
            "processing_collections": [],
            "failed_collections": [],
            "assembly": 1,
            "public": False,
            "cellCycleStage": "asynchronous",
            "protein": "CTCF",
            "valueType": "ChromatinAssociation",
            "filetype": "bigwig",
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
            "datasetName": "test",
            "assembly": "1",
            "cellCycleStage": "asynchronous",
            "perturbation": "No perturbation",
            "description": "test-description",
            "ValueType": "ChromatinAssociation",
            "processing_datasets": [],
            "Protein": "CTCF",
            "Method": "ChipSeq",
            "Normalization": "RPM",
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
            "method": "ChipSeq",
            "id": 1,
            "user_id": 1,
            "normalization": "RPM",
            "dataset_name": "test",
            "processing_state": "uploaded",
            "description": "test-description",
            "perturbation": "No perturbation",
            "file_path": "./tmp_test/1_test.bigwig",
            "processing_datasets": [],
            "failed_datasets": [],
            "processing_collections": [],
            "failed_collections": [],
            "assembly": 1,
            "public": False,
            "cellCycleStage": "asynchronous",
            "protein": "CTCF",
            "valueType": "ChromatinAssociation",
            "filetype": "bigwig",
        }
        self.assertEqual(expected, dataset.to_json())
        # test whether uploaded file exists
        self.assertTrue(os.path.exists(dataset.file_path))
        # test whether uploaded file is equal to expected file
        with open("tests/testfiles/test.bw", "rb") as expected_file, open(
            dataset.file_path, "rb"
        ) as actual_file:
            self.assertEqual(expected_file.read(), actual_file.read())

    @patch("app.api.post_routes.parse_binsizes")
    @patch("app.models.User.launch_task")
    def test_dataset_added_correctly_cooler_wo_description(
        self, mock_launch, mock_parse_binsizes
    ):
        """Tests whether a cooler dataset is added
        correctly to the Dataset table following
        a post request."""
        # add return values
        mock_parse_binsizes.return_value = [5000000]
        # construct form data
        data = {
            "datasetName": "test",
            "assembly": "1",
            "cellCycleStage": "asynchronous",
            "perturbation": "No perturbation",
            "ValueType": "Interaction",
            "Method": "HiC",
            "Normalization": "ICCF",
            "filetype": "cooler",
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
            "normalization": "ICCF",
            "dataset_name": "test",
            "processing_state": "uploaded",
            "description": "No description provided",
            "perturbation": "No perturbation",
            "file_path": "./tmp_test/1_test.mcool",
            "processing_datasets": [],
            "failed_datasets": [],
            "processing_collections": [],
            "failed_collections": [],
            "assembly": 1,
            "public": False,
            "cellCycleStage": "asynchronous",
            "valueType": "Interaction",
            "filetype": "cooler",
            "method": "HiC",
            "available_binsizes": '["5000000"]',
            "user_id": 1,
            "id": 1,
        }
        self.assertEqual(expected, dataset.to_json())
        # check whether binsizes have been added correctly -> test cooler contains single resolution with size 5 * 10**6
        self.assertEqual(json.loads(dataset.available_binsizes), ["5000000"])

    @patch("app.models.User.launch_task")
    def test_dataset_added_correctly_bed(self, mock_launch):
        """Tests whether a bed dataset is added
        correctly to the Dataset table following
        a post request."""
        # construct form data
        data = {
            "datasetName": "test",
            "assembly": "1",
            "description": "test-description",
            "cellCycleStage": "asynchronous",
            "perturbation": "No perturbation",
            "ValueType": "Derived",
            "Method": "HiC",
            "SizeType": "Interval",
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
        # check whether dataset has been added to database
        self.assertEqual(len(Dataset.query.all()), 1)
        dataset = Dataset.query.first()
        expected = {
            "dataset_name": "test",
            "processing_state": "processing",
            "description": "test-description",
            "sizeType": "Interval",
            "perturbation": "No perturbation",
            "file_path": "./tmp_test/1_test.bed",
            "processing_datasets": [],
            "failed_datasets": [],
            "processing_collections": [],
            "failed_collections": [],
            "assembly": 1,
            "public": False,
            "cellCycleStage": "asynchronous",
            "valueType": "Derived",
            "filetype": "bedfile",
            "method": "HiC",
            "user_id": 1,
            "id": 1,
        }
        self.assertEqual(expected, dataset.to_json())
        # test whether uploaded file exists
        self.assertTrue(os.path.exists(dataset.file_path))
        # test whether uploaded file is equal to expected file
        expected_file = b"abcdef"
        with open(dataset.file_path, "rb") as actual_file:
            self.assertEqual(expected_file, actual_file.read())

    @patch("app.models.User.launch_task")
    def test_incorrect_filetype_is_rejected(self, mock_launch):
        """Tests whether incorrect filetype is rejected"""
        # construct form data
        data = {
            "datasetName": "test",
            "assembly": "1",
            "description": "test-description",
            "cellCycleStage": "asynchronous",
            "perturbation": "No perturbation",
            "ValueType": "Derived",
            "Method": "HiC",
            "SizeType": "Interval",
            "filetype": "bad",
            "file": (io.BytesIO(b"abcdef"), "test.bed"),
            "Directionality": "-",
        }
        # dispatch post request
        response = self.client.post(
            "/api/datasets/",
            data=data,
            headers=self.token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    @patch("app.models.User.launch_task")
    def test_bed_pipeline_launched_correctly(self, mock_launch):
        """Tests whether bed pipeline is called with the right arguments."""
        # construct form data
        data = {
            "datasetName": "test",
            "assembly": "1",
            "description": "test-description",
            "cellCycleStage": "asynchronous",
            "perturbation": "No perturbation",
            "ValueType": "Derived",
            "Method": "HiC",
            "SizeType": "Interval",
            "filetype": "bedfile",
            "file": (io.BytesIO(b"abcdef"), "test.bed"),
            "Directionality": "-",
        }
        # dispatch post request
        response = self.client.post(
            "/api/datasets/",
            data=data,
            headers=self.token_headers,
            content_type="multipart/form-data",
        )
        # check whether launch task has been called with the right arguments
        mock_launch.assert_called_with("pipeline_bed", "run bed preprocessing", 1)

    def test_badform_no_datasetName(self):
        """Tests whether form without datasetName is rejected"""
        # construct form data
        data = {
            "assembly": "1",
            "description": "test-description",
            "cellCycleStage": "asynchronous",
            "perturbation": "No perturbation",
            "ValueType": "Derived",
            "Method": "HiC",
            "SizeType": "Interval",
            "filetype": "bedfile",
            "file": (io.BytesIO(b"abcdef"), "test.bed"),
            "Directionality": "-",
        }
        # dispatch post request
        response = self.client.post(
            "/api/datasets/",
            data=data,
            headers=self.token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    def test_badform_no_fileObject(self):
        """Tests whether form without file is rejected"""
        # construct form data
        data = {
            "datasetName": "IE",
            "assembly": "1",
            "description": "test-description",
            "cellCycleStage": "asynchronous",
            "perturbation": "No perturbation",
            "ValueType": "Derived",
            "Method": "HiC",
            "SizeType": "Interval",
            "filetype": "bedfile",
            "Directionality": "-",
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
            "datasetName": "test",
            "assembly": "1",
            "description": "test-description",
            "cellCycleStage": "asynchronous",
            "perturbation": "No perturbation",
            "ValueType": "Derived",
            "Method": "HiC",
            "SizeType": "Interval",
            "filetype": "bedfile",
            "file": (io.BytesIO(b"abcdef"), "test.mcool"),
            "Directionality": "-",
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
            "datasetName": "test",
            "description": "test-description",
            "assembly": "1",
            "cellCycleStage": "asynchronous",
            "perturbation": "No perturbation",
            "ValueType": "Interaction",
            "Method": "HiC",
            "Normalization": "ICCF",
            "filetype": "cooler",
            "file": (open("tests/testfiles/test.mcool", "rb"), "test.bed"),
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
            "datasetName": "test",
            "assembly": "1",
            "description": "test-description",
            "cellCycleStage": "asynchronous",
            "perturbation": "No perturbation",
            "ValueType": "SetIdentity",
            "Method": "HiC",
            "SizeType": "Interval",
            "filetype": "bedfile",
            "file": (io.BytesIO(b"abcdef"), "test"),
            "Directionality": "-",
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
            "datasetName": "test",
            "assembly": "1",
            "description": "test-description",
            "cellCycleStage": "asynchronous",
            "perturbation": "No perturbation",
            "ValueType": "SetIdentity",
            "Method": "HiC",
            "SizeType": "Interval",
            "filetype": "bedfile",
            "file": open("tests/testfiles/wrongly_formatted_bedfile.bed", "rb"),
            "Directionality": "-",
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
            "datasetName": "test",
            "description": "test-description",
            "assembly": "1",
            "cellCycleStage": "asynchronous",
            "perturbation": "No perturbation",
            "ValueType": "Interaction",
            "Method": "HiC",
            "Normalization": "ICCF",
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

    @patch("app.models.User.launch_task")
    def test_public_flag_set_correctly_if_true(self, mock_launch_task):
        """Tests whether form with file without ending is rejected."""
        # construct form data
        data = {
            "datasetName": "test",
            "assembly": "1",
            "description": "test-description",
            "cellCycleStage": "asynchronous",
            "perturbation": "No perturbation",
            "ValueType": "Derived",
            "public": "true",
            "Method": "HiC",
            "SizeType": "Interval",
            "filetype": "bedfile",
            "file": (io.BytesIO(b"abcdef"), "test.bed"),
            "Directionality": "-",
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

    @patch("app.models.User.launch_task")
    def test_public_flag_set_correctly_if_false(self, mock_launch_task):
        """Tests whether form with file without ending is rejected."""
        # construct form data
        data = {
            "datasetName": "test",
            "assembly": "1",
            "description": "test-description",
            "cellCycleStage": "asynchronous",
            "perturbation": "No perturbation",
            "ValueType": "Derived",
            "public": "false",
            "Method": "HiC",
            "SizeType": "Interval",
            "filetype": "bedfile",
            "file": (io.BytesIO(b"abcdef"), "test.bed"),
            "Directionality": "-",
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
