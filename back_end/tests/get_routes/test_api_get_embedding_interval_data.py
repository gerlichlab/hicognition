"""Tests for get route of embedding interval data."""
import os
import gzip
import json
import unittest
import numpy as np
from hicognition.test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
# import sys
# sys.path.append("./")
from app import db
from app.models import Dataset, Intervals, EmbeddingIntervalData


class TestGetEmbeddingIntervalData(LoginTestCase, TempDirTestCase):
    """Tests for get route of embedding interval data."""

    def setUp(self):
        super().setUp()
        # add owned collection
        self.owned_cooler = Dataset(id=1, user_id=1, filetype="cooler")
        # add unowned collection
        self.unowned_cooler = Dataset(id=2, user_id=2, filetype="cooler")
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
        self.embed_data_cooler_unowned = EmbeddingIntervalData(
            id=1,
            binsize=10000,
            dataset_id=self.unowned_cooler.id,
            intervals_id=self.owned_intervals.id,
            value_type="2d-embedding",
        )
        # add averageIntervalData with unowned intervals
        self.embed_data_intervals_unowned = EmbeddingIntervalData(
            id=2,
            binsize=10000,
            dataset_id=self.owned_cooler.id,
            intervals_id=self.unowned_intervals.id,
            value_type="2d-embedding",
        )
        # add embeddingIntervalData with owned intervals and collection and associated data
        self.test_data = np.array(
            [[1.0, 2.0], [3, 4.0], [5.0, 6.0], [7.0, 8.0], [9.0, 10.0], [11.0, 12.0]]
        )
        data_path = os.path.join(TempDirTestCase.TEMP_PATH, "test.npy")
        np.save(data_path, self.test_data)
        # create thumbnails
        thumbnails = [
            np.array([[5.0, 6.0], [7.0, 7.0]]),
            np.array([[1.0, 2.0], [3.0, 4.0]]),
            np.array([[1.5, 10.0], [7.0, 3.4]]),
        ]
        self.thumbnail_data = np.stack(thumbnails)
        thumbnail_path = os.path.join(TempDirTestCase.TEMP_PATH, "test_thumbnails.npy")
        np.save(thumbnail_path, self.thumbnail_data)
        # create clusters
        self.cluster_data = np.array([1.0, 2.0, 3.0, 1.0, 1.0, 2.0])
        cluster_path = os.path.join(TempDirTestCase.TEMP_PATH, "test_clusters.npy")
        np.save(cluster_path, self.cluster_data)
        # create distributions
        self.distribution_data = np.array(
            [[0.1, 0.2, 0.7], [0.4, 0.2, 0.4], [0.1, 0.1, 0.8]]
        )
        distribution_path = os.path.join(
            TempDirTestCase.TEMP_PATH, "test_distribution.npy"
        )
        np.save(distribution_path, self.distribution_data)
        # create data
        self.embedding_data_owned = EmbeddingIntervalData(
            id=3,
            binsize=10000,
            file_path=data_path,
            dataset_id=self.owned_cooler.id,
            intervals_id=self.owned_intervals.id,
            thumbnail_path=thumbnail_path,
            cluster_id_path=cluster_path,
            feature_distribution_path=distribution_path,
            value_type="2d-embedding",
        )

    def test_no_auth(self):
        """No authentication provided, response should be 401"""
        # protected route
        response = self.client.get(
            "/api/embeddingIntervalData/1/", content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

    def test_embedding_interval_data_does_not_exist(self):
        """Test 404 is returned if embeddingIntervalData does not exist."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # make request
        response = self.client.get(
            "/api/embeddingIntervalData/500/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_dataset_not_owned(self):
        """Cooler dataset underlying embeddingIntervalData is not owned"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        db.session.add_all(
            [
                self.owned_bedfile,
                self.unowned_cooler,
                self.owned_intervals,
                self.embed_data_cooler_unowned,
            ]
        )
        db.session.commit()
        # make request for forbidden cooler
        response = self.client.get(
            f"/api/embeddingIntervalData/{self.embed_data_cooler_unowned.id}/",
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
                self.owned_cooler,
                self.unowned_bedfile,
                self.unowned_intervals,
                self.embed_data_intervals_unowned,
            ]
        )
        db.session.commit()
        # make request with forbidden intervall
        response = self.client.get(
            f"/api/embeddingIntervalData/{self.embed_data_intervals_unowned.id}/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_correct_data_returned(self):
        """Correct data is returned from an owned embeddingIntervalData"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        db.session.add_all(
            [
                self.owned_cooler,
                self.owned_bedfile,
                self.owned_intervals,
                self.embeddingData_owned,
            ]
        )
        db.session.commit()
        # make request
        response = self.client.get(
            f"/api/embeddingIntervalData/{self.embeddingData_owned.id}/",
            headers=token_headers,
            content_type="application/json",
        )
        data = json.loads(gzip.decompress(response.data))
        expected = {
            "embedding": {
                "data": self.test_data.flatten().tolist(),
                "shape": list(self.test_data.shape),
                "dtype": "float32",
            },
            "cluster_ids": {
                "data": self.cluster_data.tolist(),
                "shape": list(self.cluster_data.shape),
                "dtype": "float32",
            },
            "thumbnails": {
                "data": self.thumbnail_data.flatten().tolist(),
                "shape": list(self.thumbnail_data.shape),
                "dtype": "float32",
            },
        }
        self.assertEqual(data, expected)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
