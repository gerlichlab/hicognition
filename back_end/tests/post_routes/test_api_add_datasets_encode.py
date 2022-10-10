"""Module with tests realted adding datasets."""
import os
import io
import json
import unittest
import time
from unittest.mock import patch

import requests


# add path to import app
# import sys
# sys.path.append("./")
from app.models import (
    Dataset,
    Assembly,
    DataRepository,
    User_DataRepository_Credentials,
)
from app import db, create_app
from hicognition.test_helpers import LoginTestCase, TempDirTestCase


class TestAddDataSetsEncode(LoginTestCase, TempDirTestCase):
    """TODO"""

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
            "datasetName": "test",
            "description": "test-description",
            "assembly": "1",
            "cellCycleStage": "asynchronous",
            "perturbation": "No perturbation",
            "ValueType": "Peak",
            "Method": "ChipSeq",
            "SizeType": "Point",
            "filetype": "bedfile",
            "Directionality": "+",
            "public": "false",
            "sampleID": "4DNFIRCHWS8M",
            "repositoryName": "testrepo",
            "user_id": 1,
        }

    def mock_http_request(*args, **kwargs):
        class MockResponse:
            def __init__(self, content, status_code, headers={}):
                self.content = content
                self.status_code = status_code
                self.headers = headers

            def raise_for_status(self):
                if self.status_code >= 400:
                    raise requests.HTTPError(f"Mock HTTPError {self.status_code}")
                return

        if args[0] == "https://4DNFIRCHWS8M.bed.gz":
            with open("tests/testfiles/4DNFIRCHWS8M.bed.gz", "rb") as file:
                return MockResponse(
                    file.read(),
                    200,
                    headers={"Content-Disposition": "filename=filename.json"},
                )
        if args[0] == "https://4DNFIRCHWS8M" and args[1] == {
            "Accept": "application/json"
        }:
            with open("tests/testfiles/4DNFIRCHWS8M.json", "r") as file:
                return MockResponse(
                    file.read(), 200, headers={"Application": "application/json"}
                )
        if args[0] == "https://test.bw":
            with open("tests/testfiles/test.bw", "rb") as file:
                return MockResponse(
                    file.read(),
                    200,
                    headers={"Content-Disposition": "filename=filename.json"},
                )
        return MockResponse("", 404)

    def test_repo_not_found(self):
        data = self.default_data
        data["repositoryName"] = "not_there"

        response = self.client.post(
            "/api/datasets/encode/",
            data=data,
            headers=self.token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)
        # self.assertTrue(f'Repository {data["repositoryName"]} not found.' in response.)

    @patch("app.models.User.launch_task")
    @patch("requests.get", side_effect=mock_http_request)
    def test_load_bed_file_from_repo(self, mock_http_request, mock_launch):
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
        self.assertEqual(dataset.repository_name, self.default_data["repositoryName"])
        self.assertEqual(dataset.repository, self.data_repo)
        self.assertEqual(dataset.processing_state, "uploading")

    @patch("requests.get", side_effect=mock_http_request)
    def test_unknown_user_cant_add(self, mock_http_request):
        data = self.default_data
        data["user"] = 22
        response = self.client.post(
            "/api/datasets/encode/",
            data=data,
            headers=self.token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)
        # check whether dataset has been added to database
        self.assertEqual(len(Dataset.query.all()), 0)

    def test_form_validation(self):
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
        self.assertEqual(dataset.repository_name, self.default_data["repositoryName"])
        self.assertEqual(dataset.repository, self.data_repo)
        self.assertEqual(dataset.processing_state, "uploading")
