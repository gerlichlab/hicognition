"""Testfile for tasks.download_dataset_file.
TODO more tests?
"""

import unittest
from unittest.mock import patch
from hicognition.test_helpers import LoginTestCase, TempDirTestCase
from app import db
from app.models import *
from app.tasks import download_dataset_file


class TestDownloadDatasetFile(LoginTestCase, TempDirTestCase):
    """Tests task for downloading dataset files"""

    def setUp(self):
        super(TestDownloadDatasetFile, self).setUp()
        self.assembly = Assembly(
            id=1,
            name="hg19",
            chrom_sizes=self.app.config["CHROM_SIZES"],
            chrom_arms=self.app.config["CHROM_ARMS"],
        )
        db.session.add(self.assembly)
        self.repository = Repository(
            file_url="{id}", url="{href}", name="repo_name"
        )
        db.session.add(self.repository)

        self.dataset = self.create_dataset(id=1, dataset_name="ds1", filetype="bedfile")
        self.dataset.user = User(id=2)
        self.dataset.repository = self.repository
        self.dataset.assembly = self.assembly.id
        db.session.add(self.dataset)

        db.session.commit()

    test_cases = {
        "valid_url": {"preprocessed"},
        "valid_samples": {"preprocessed"},
        "valid_url": {"preprocessed"},
        "valid_url": {"preprocessed"},
    }

    @patch("app.tasks._handle_error")
    def test_dataset_not_found(self, mock_error):
        download_dataset_file(123123)
        self.assertTrue(mock_error.called)

    @patch("app.tasks._handle_error")
    @patch("app.models.Dataset.query.get")
    def test_invalid_inputs(self, mock_get_dataset, mock_error):
        test_cases = {
            "none": {},
            "sample_id_only": {"sample_id": "asdf"},
            "sample_repo_only": {"repository_name": "asdf"},
            "sample_all_three": {
                "sample_id": "asdf",
                "repository_name": "asdf",
                "source_url": "https://asdfasdfasdfasdfa.at",
            },
        }
        for key, test_case in test_cases.items():
            with self.subTest(tc=key):
                dataset = self.dataset
                dataset.sample_id = test_case.get("sample_id")
                dataset.repository_name = test_case.get("repository_name")
                dataset.source_url = test_case.get("source_url")
                mock_get_dataset.return_value = dataset

                download_dataset_file(1)
                self.assertTrue(mock_error.called)
                mock_error.reset_mock()

    @patch("app.models.Dataset.preprocess_dataset")
    @patch("app.models.Dataset.validate_dataset")
    @patch("app.download_utils.download_url")
    @patch("app.download_utils.download_encode")
    @patch("app.models.Dataset.query.get")
    def test_valid_inputs(
        self,
        mock_get_dataset,
        mock_download_url,
        mock_download_encode,
        mock_validate,
        mock_preprocess,
    ):
        test_cases = {
            "url": {"source_url": "http://urlurl1337url.at"},
            "encode": {"sample_id": "asdf", "repository_name": "asdf"},
        }
        for key, test_case in test_cases.items():
            with self.subTest(tc=key):
                dataset = self.dataset
                dataset.sample_id = test_case.get("sample_id")
                dataset.repository_name = test_case.get("repository_name")
                dataset.source_url = test_case.get("source_url")
                mock_get_dataset.return_value = dataset
                download_dataset_file(1)

                self.assertTrue(mock_preprocess.called)
                mock_preprocess.reset_mock()


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
