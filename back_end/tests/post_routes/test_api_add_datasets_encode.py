"""Module with tests realted adding datasets."""
import json
import unittest
from unittest.mock import patch


# add path to import app
# import sys
# sys.path.append("./")
from app.models import Dataset, Assembly, DataRepository
from app import db
from hicognition.test_helpers import LoginTestCase, TempDirTestCase


class TestAddDataSetsEncode(LoginTestCase, TempDirTestCase):
    """Tests route that adds Datasets using encode repo and sample id.
    Form validation tested extensively in test_api_add_datasets
    This tests:
    - Further form validation
    - repo not found
    - returned metadata is 404 or similar
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
            name="testrepo",
            url="https://{href}",
            auth_required=False,
            file_url="https://{id}",
        )
        db.session.add(self.hg19)
        db.session.add(self.data_repo)
        db.session.commit()

        self.token_headers = self.get_token_header(
            self.add_and_authenticate("test", "asdf")
        )
        self.token_headers["Content-Type"] = "multipart/form-data"

        self.default_data = {
            "dataset_name": "test",
            "description": "test-description",
            "assembly": "1",
            "filetype": "bedfile",
            "public": "false",
            "sample_id": "4DNFIRCHWS8M",
            "repository_name": "testrepo",
            "sizeType": "point",
            "dataset_type": "region",
            "metadata_json": json.dumps({
                "Cell cycle Stage": "asynchronous",
                "Perturbation": "No perturbation",
                "ValueType": "Peak",
                "Method": "ChipSeq",
                "Size Type": "Point",
                "Directionality": "+",
            })
        }

    def test_repo_not_found(self):
        data = self.default_data
        data["repository_name"] = "not_there"

        response = self.client.post(
            "/api/datasets/encode/",
            data=data,
            headers=self.token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    @patch("app.models.User.launch_task")
    @patch("app.download_utils.download_ENCODE_metadata")
    def test_form_validity(self, mock_get_metadata, mock_launch):
        mock_get_metadata.return_value = {"status_code": 200}
        test_cases = {
            "default": {
                "data": self.default_data,
                "code": 200,
                "msg": "success",
                "return_value": {"status_code": 200},
            },
            "filetype_notsupported": {
                "data": {**self.default_data, "filetype": "notsupp"},
                "code": 400,
                "msg": "Form is not valid",
                "return_value": {"status_code": 400},
            },
            "no_public": {
                "data": {**self.default_data, "public": ""},
                "code": 400,
                "msg": "Form is not valid",
                "return_value": {"status_code": 400},
            },
            "no_sampleid": {
                "data": {**self.default_data, "sample_id": ""},
                "code": 400,
                "msg": "Form is not valid",
                "return_value": {"status_code": 400},
            },
            "repo_not_found": {
                "data": {**self.default_data, "repository_name": "nonexsitant"},
                "code": 400,
                "msg": "Repository",
                "return_value": {"status_code": 400},
            },
            "no_repo": {
                "data": {**self.default_data, "repository_name": ""},
                "code": 400,
                "msg": "Repository",
                "return_value": {"status_code": 400},
            }
        }

        for key, test_case in test_cases.items():
            mock_get_metadata.return_value = test_case["return_value"]
            with self.subTest(test_case=test_case):
                response = self.client.post(
                    "/api/datasets/encode/",
                    data=test_case["data"],
                    headers=self.token_headers,
                    content_type="multipart/form-data",
                )
                self.assertEqual(response.status_code, test_case["code"])
                response_data = response.get_json()
                self.assertTrue(test_case["msg"] in response_data["message"])

    @patch("app.models.User.launch_task")
    @patch("app.download_utils.download_ENCODE_metadata")
    def test_load_bed_file_from_repo(self, mock_get_metadata, mock_launch):
        mock_get_metadata.return_value = {"status_code": 200}
        data = self.default_data
        response = self.client.post(
            "/api/datasets/encode/",
            data=data,
            headers=self.token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(Dataset.query.all()), 1)

        dataset = Dataset.query.first()
        self.assertEqual(dataset.repository_name, self.default_data["repository_name"])
        self.assertEqual(dataset.repository, self.data_repo)
        self.assertEqual(dataset.processing_state, "new")


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
