import os
import gzip
import json
import unittest
import numpy as np
from test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
import sys

sys.path.append("./")
from app import db
from app.models import Collection, Dataset, Intervals, EmbeddingIntervalData


class TestGetEmbeddingIntervalDataThumbnails(LoginTestCase, TempDirTestCase):
    """Tests for get route of thumbnails associated with embeddingIntervalData"""

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
        self.embeddingData_collection_unowned = EmbeddingIntervalData(
            id=1,
            binsize=10000,
            collection_id=self.unowned_collection.id,
            intervals_id=self.owned_intervals.id,
        )
        # add embeddingIntervalData with unowned intervals
        self.embeddingData_intervals_unowned = EmbeddingIntervalData(
            id=2,
            binsize=10000,
            collection_id=self.owned_collection.id,
            intervals_id=self.unowned_intervals.id,
        )
        # add owned embeddingIntervalData without thumbnails/feature_id and cluster_did
        self.embeddingData_intervals_wo_thumbnail_data = EmbeddingIntervalData(
            id=4,
            binsize=10000,
            collection_id=self.owned_collection.id,
            intervals_id=self.owned_intervals.id,
        )
        # add embeddingIntervalData with owned intervals and collection and associated data
        self.test_data = np.array([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10], [11, 12]])
        data_path = os.path.join(TempDirTestCase.TEMP_PATH, "test.npy")
        np.save(data_path, self.test_data)
        # create thumbnails
        thumbnails = [np.array([[5, 6], [ 7, 7]]), np.array([[1, 2], [3, 4]]), np.array([[1.5, 10], [7.0, 3.4]])]
        self.thumbnail_data = np.stack(thumbnails)
        thumbnail_path = os.path.join(TempDirTestCase.TEMP_PATH, "test_thumbnails.npy")
        np.save(thumbnail_path, self.thumbnail_data)
        # create clusters
        self.cluster_data = np.array([1, 2, 3, 1, 1, 2])
        cluster_path = os.path.join(TempDirTestCase.TEMP_PATH, "test_clusters.npy")
        np.save(cluster_path, self.cluster_data)
        # create distributions
        self.distribution_data = np.array(
            [[0.1, 0.2, 0.7], [0.4, 0.2, 0.4], [0.1, 0.1, 0.8]]
        )
        distribution_path = os.path.join(TempDirTestCase.TEMP_PATH, "test_clusters.npy")
        np.save(distribution_path, self.distribution_data)
        # create data
        self.embeddingData_owned = EmbeddingIntervalData(
            id=3,
            binsize=10000,
            file_path=data_path,
            collection_id=self.owned_collection.id,
            intervals_id=self.owned_intervals.id,
            thumbnail_path=thumbnail_path,
            cluster_id_path=cluster_path,
            feature_distribution_path=distribution_path,
        )

    def test_no_auth(self):
        """No authentication provided, response should be 401"""
        # protected route
        response = self.client.get(
            "/api/embeddingIntervalData/1/thumbnail/0/", content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

    def test_embeddingIntervalData_does_not_exist(self):
        """Test 404 is returned if embeddingIntervalData does not exist."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # make request
        response = self.client.get(
            "/api/embeddingIntervalData/500/thumbnail/0/",
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
                self.embeddingData_collection_unowned,
            ]
        )
        db.session.commit()
        # make request for forbidden cooler
        response = self.client.get(
            f"/api/embeddingIntervalData/{self.embeddingData_collection_unowned.id}/thumbnail/0/",
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
                self.embeddingData_intervals_unowned,
            ]
        )
        db.session.commit()
        # make request with forbidden intervall
        response = self.client.get(
            f"/api/embeddingIntervalData/{self.embeddingData_intervals_unowned.id}/thumbnail/0/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_thumbnail_file_does_not_exist(self):
        """Route returns 404 if thumbnail file does not exist"""
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
                self.embeddingData_intervals_wo_thumbnail_data,
            ]
        )
        db.session.commit()
        # make request with forbidden intervall
        response = self.client.get(
            f"/api/embeddingIntervalData/{self.embeddingData_intervals_wo_thumbnail_data.id}/thumbnail/0/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_thumbnail_index_is_out_of_range(self):
        """Route returns 404 if thumbnail index is out of range"""
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
                self.embeddingData_owned,
            ]
        )
        db.session.commit()
        # make request with forbidden intervall
        response = self.client.get(
            f"/api/embeddingIntervalData/{self.embeddingData_owned.id}/thumbnail/10/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_correct_data_returned_index_0(self):
        """Correct data is returned from an owned embeddingIntervalData"""
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
                self.embeddingData_owned,
            ]
        )
        db.session.commit()
        # make request
        response = self.client.get(
            f"/api/embeddingIntervalData/{self.embeddingData_owned.id}/thumbnail/0/",
            headers=token_headers,
            content_type="application/json",
        )
        expected = {
            "heatmap": {
                "data": self.thumbnail_data[0, :].flatten().tolist(),
                "shape": list(self.thumbnail_data[0, :].shape),
                "dtype": "float32",
            },
            "distribution": self.distribution_data[0, :].tolist(),
        }
        data = json.loads(gzip.decompress(response.data))
        self.assertEqual(data, expected)

    def test_correct_data_returned_index_2(self):
        """Correct data is returned from an owned embeddingIntervalData"""
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
                self.embeddingData_owned,
            ]
        )
        db.session.commit()
        # make request
        response = self.client.get(
            f"/api/embeddingIntervalData/{self.embeddingData_owned.id}/thumbnail/2/",
            headers=token_headers,
            content_type="application/json",
        )
        expected = {
            "heatmap": {
                "data": self.thumbnail_data[2, :].flatten().tolist(),
                "shape": list(self.thumbnail_data[2, :].shape),
                "dtype": "float32",
            },
            "distribution": self.distribution_data[2, :].tolist(),
        }
        data = json.loads(gzip.decompress(response.data))
        self.assertEqual(data, expected)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
