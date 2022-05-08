"""Tests for get route of features associated with embedding interval data."""
import os
import gzip
import json
import unittest
from unittest.mock import patch
import numpy as np
from hicognition.test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
# import sys
# sys.path.append("./")
from app import db
from app.models import Collection, Dataset, Intervals, EmbeddingIntervalData


class TestGetEmbeddingIntervalDataFeatures(LoginTestCase, TempDirTestCase):
    """Tests for get route of features associated with embedding interval data."""

    def setUp(self):
        super().setUp()
        # add owned collection
        self.owned_collection = Collection(id=1, user_id=1)
        # add unowned collection
        self.unowned_collection = Collection(id=2, user_id=2)
        # add owned bedfile
        self.owned_bedfile = Dataset(id=3, filetype="bedfile", user_id=1)
        # add unowned bedfile
        self.unowned_bedfile = Dataset(id=4, filetype="bedfile", user_id=2)
        # add intervals for owned bedfile
        self.owned_intervals = Intervals(
            id=1, dataset_id=self.owned_bedfile.id, windowsize=200000
        )
        # add intervals for unowned bedfile
        self.unowned_intervals = Intervals(
            id=2, dataset_id=self.unowned_bedfile.id, windowsize=200000
        )
        # add embeddingIntervalData with unowned collection
        self.assoc_data_collection_unowned = EmbeddingIntervalData(
            id=1,
            binsize=10000,
            collection_id=self.unowned_collection.id,
            intervals_id=self.owned_intervals.id,
        )
        # add averageIntervalData with unowned intervals
        self.assoc_data_intervals_unowned = EmbeddingIntervalData(
            id=2,
            binsize=10000,
            collection_id=self.owned_collection.id,
            intervals_id=self.unowned_intervals.id,
        )
        # add embeddingIntervalData with owned intervals and collection and associated data
        self.test_data = np.array([[1.66, 2.2, 3.8, 4.5]])
        data_path = os.path.join(TempDirTestCase.TEMP_PATH, "test.npy")
        np.save(data_path, self.test_data)
        self.feature_data = np.array([[5.0, 6.0, 7.0, 8.0], [1.0, 2.0, 3.0, 4.0]])
        feature_path = os.path.join(TempDirTestCase.TEMP_PATH, "test_features.npy")
        np.save(feature_path, self.feature_data)
        self.assoc_data_owned = EmbeddingIntervalData(
            id=3,
            binsize=10000,
            file_path=data_path,
            collection_id=1,
            intervals_id=1,
            file_path_feature_values=feature_path,
        )

    def test_no_auth(self):
        """No authentication provided, response should be 401"""
        # protected route
        response = self.client.get(
            "/api/embeddingIntervalData/1/0/", content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

    def test_no_auth_required_showcase(self):
        """No authentication required showcase user"""
        app_config = self.app.config.copy()
        app_config["SHOWCASE"] = True
        with patch("app.api.authentication.current_app.config") as mock_config:
            mock_config.__getitem__.side_effect = app_config.__getitem__
            # dispatch call
            response = self.client.get(
                "/api/embeddingIntervalData/500/0/", content_type="application/json"
            )
            self.assertEqual(response.status_code, 404)

    def test_embedding_interval_data_does_not_exist(self):
        """Test 404 is returned if embeddingIntervalData does not exist."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # make request
        response = self.client.get(
            "/api/embeddingIntervalData/500/0/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_collection_not_owned(self):
        """Collection underlying embeddingIntervalData is not owned"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        db.session.add_all(
            [
                self.owned_bedfile,
                self.unowned_collection,
                self.owned_intervals,
                self.assoc_data_collection_unowned,
            ]
        )
        db.session.commit()
        # make request for forbidden cooler
        response = self.client.get(
            f"/api/embeddingIntervalData/{self.assoc_data_collection_unowned.id}/0/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_intervals_not_owned(self):
        """Intervals dataset underlying embeddingIntervalData are not owned"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        db.session.add_all(
            [
                self.owned_collection,
                self.unowned_bedfile,
                self.unowned_intervals,
                self.assoc_data_intervals_unowned,
            ]
        )
        db.session.commit()
        # make request with forbidden intervall
        response = self.client.get(
            f"/api/embeddingIntervalData/{self.assoc_data_intervals_unowned.id}/0/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_correct_data_returned_index_0(self):
        """Correct feature data is returned from an owned embeddingIntervalData"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        db.session.add_all(
            [
                self.owned_collection,
                self.owned_bedfile,
                self.owned_intervals,
                self.assoc_data_owned,
            ]
        )
        db.session.commit()
        # make request
        response = self.client.get(
            f"/api/embeddingIntervalData/{self.assoc_data_owned.id}/0/",
            headers=token_headers,
            content_type="application/json",
        )
        data = json.loads(gzip.decompress(response.data))
        expected = {
            "data": self.feature_data[:, 0].flatten().tolist(),
            "shape": list(self.feature_data[:, 0].shape),
            "dtype": "float32",
        }
        self.assertEqual(data, expected)

    def test_correct_data_returned_index_0_showcase(self):
        """Correct feature data is returned from an owned embeddingIntervalData"""
        app_config = self.app.config.copy()
        app_config["SHOWCASE"] = True
        with patch("app.api.authentication.current_app.config") as mock_config:
            mock_config.__getitem__.side_effect = app_config.__getitem__
            # add data
            db.session.add_all(
                [
                    self.owned_collection,
                    self.owned_bedfile,
                    self.owned_intervals,
                    self.assoc_data_owned,
                ]
            )
            db.session.commit()
            # make request
            response = self.client.get(
                f"/api/embeddingIntervalData/{self.assoc_data_owned.id}/0/",
                content_type="application/json",
            )
            data = json.loads(gzip.decompress(response.data))
            expected = {
                "data": self.feature_data[:, 0].flatten().tolist(),
                "shape": list(self.feature_data[:, 0].shape),
                "dtype": "float32",
            }
            self.assertEqual(data, expected)

    def test_correct_data_returned_index_2(self):
        """Correct feature data is returned from an owned embeddingIntervalData"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        db.session.add_all(
            [
                self.owned_collection,
                self.owned_bedfile,
                self.owned_intervals,
                self.assoc_data_owned,
            ]
        )
        db.session.commit()
        # make request
        response = self.client.get(
            f"/api/embeddingIntervalData/{self.assoc_data_owned.id}/2/",
            headers=token_headers,
            content_type="application/json",
        )
        data = json.loads(gzip.decompress(response.data))
        expected = {
            "data": self.feature_data[:, 2].flatten().tolist(),
            "shape": list(self.feature_data[:, 2].shape),
            "dtype": "float32",
        }
        self.assertEqual(data, expected)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
