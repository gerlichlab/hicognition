"""Tests for /api/datasets/processing route to list processing datasets."""
import unittest
from unittest.mock import patch
import pandas as pd
from tests.test_utils.test_helpers import LoginTestCase

# add path to import app
# import sys
# sys.path.append("./")
from app import db
from app.models import Dataset, Session, Collection


class TestGetProcessingDatasets(LoginTestCase):
    """Test cases for processing datasets"""


    def setUp(self):
        super().setUp()
        # add bedfiles
        self.bedfile_processing_features = self.create_dataset(
            id=1,
            user_id=1,
            filetype="bedfile",
            dataset_name="testfile",
            upload_state="uploaded"
        )
        self.bedfile_processing_collections = self.create_dataset(
            id=2,
            user_id=1,
            filetype="bedfile",
            dataset_name="testfile",
            upload_state="uploaded"
        )
        self.bedfile_finished = self.create_dataset(
            id=3,
            user_id=1,
            filetype="bedfile",
            dataset_name="testfile",
            upload_state="uploaded"
        )
        self.bedfile_not_owned = self.create_dataset(
            id=4,
            user_id=1,
            filetype="bedfile",
            dataset_name="testfile",
            upload_state="uploaded"
        )
        # add features
        self.features = [
            self.create_dataset(id=i, user_id=1, filetype="bigwig", dataset_name=f"dataset_{i}", upload_state="uploaded") for i in range(5,7)
        ]
        self.features_uploading = [
            self.create_dataset(id=i, user_id=1, filetype="bigwig", dataset_name=f"dataset_{i}", upload_state='uploading') for i in range(7, 10)
        ]
        self.bedfile_processing_features.processing_features = self.features
        # add collections
        self.collections = [
            Collection(id=i) for i in range(1, 4)
        ]
        self.bedfile_processing_collections.processing_collections = self.collections


    def test_no_auth(self):
        """No authentication provided, response should be 401"""
        # protected route
        response = self.client.get(
            "/api/datasets/processing/", content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

    def test_datasets_w_processing_features_returned(self):
        """Tests whether correct files are returned"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add datasets
        db.session.add_all([self.bedfile_processing_features, self.bedfile_finished, self.bedfile_not_owned])
        db.session.commit()
        # dispatch call
        response = self.client.get(
            "/api/datasets/processing/", content_type="application/json", headers=token_headers
        )
        self.assertEqual(response.status_code, 200)
        # test
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]['id'], self.bedfile_processing_features.id)

    def test_datasets_w_processing_collections_returned(self):
        """Tests whether correct files are returned"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add datasets
        db.session.add_all([self.bedfile_processing_collections, self.bedfile_finished, self.bedfile_not_owned])
        db.session.commit()
        # dispatch call
        response = self.client.get(
            "/api/datasets/processing/", content_type="application/json", headers=token_headers
        )
        self.assertEqual(response.status_code, 200)
        # test
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]['id'], self.bedfile_processing_collections.id)

    def test_uploading_datasets_returned(self):
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)       
        # add datasets
        db.session.add_all(self.features_uploading)
        db.session.commit()
        # dispatch call
        response = self.client.get(
            "/api/datasets/processing/", content_type="application/json", headers=token_headers
        )
        self.assertEqual(response.status_code, 200)
        # test
        self.assertEqual(len(response.json), 3)