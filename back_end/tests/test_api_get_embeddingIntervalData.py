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


class TestGetEmbeddingIntervalData(LoginTestCase, TempDirTestCase):
    """Tests for get route of embedding interval data."""

    def setUp(self):
        super().setUp()
        # add owned collection
        self.owned_collection = Collection(id=1, user_id=1)
        # add unowned collection
        self.unowned_collection = Collection(id=2, user_id=2)
        # add owned bedfile
        self.owned_bedfile = Dataset(
            id=3,
            filetype="bedfile",
            user_id=1,
        )
        # add unowned bedfile
        self.unowned_bedfile = Dataset(
            id=4,
            filetype="bedfile",
            user_id=2,
        )
        # add intervals for owned bedfile
        self.owned_intervals = Intervals(
            id=1,
            dataset_id=self.owned_bedfile.id,
            windowsize=200000,
        )
        # add intervals for unowned bedfile
        self.unowned_intervals = Intervals(
            id=2,
            dataset_id=self.unowned_bedfile.id,
            windowsize=200000,
        )
        # add embeddingIntervalData with unowned collection
        self.assocData_collection_unowned = EmbeddingIntervalData(
            id=1,
            binsize=10000,
            collection_id=self.unowned_collection.id,
            intervals_id=self.owned_intervals.id,
        )
        # add averageIntervalData with unowned intervals
        self.assocData_intervals_unowned = EmbeddingIntervalData(
            id=2,
            binsize=10000,
            collection_id=self.owned_collection.id,
            intervals_id=self.unowned_intervals.id,
        )
        # add embeddingIntervalData with owned intervals and collection and associated data
        self.test_data = np.array([[1.66, 2.2, 3.8, 4.5]])
        data_path = os.path.join(TempDirTestCase.TEMP_PATH, "test.npy")
        np.save(data_path, self.test_data)
        self.assocData_owned = EmbeddingIntervalData(
            id=3,
            binsize=10000,
            file_path=data_path,
            collection_id=1,
            intervals_id=1,
        )

    def test_no_auth(self):
        """No authentication provided, response should be 401"""
        # protected route
        response = self.client.get(
            "/api/embeddingIntervalData/1/", content_type="application/json"
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
            "/api/embeddingIntervalData/500/",
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
                self.assocData_collection_unowned,
            ]
        )
        db.session.commit()
        # make request for forbidden cooler
        response = self.client.get(
            f"/api/embeddingIntervalData/{self.assocData_collection_unowned.id}/",
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
                self.assocData_intervals_unowned,
            ]
        )
        db.session.commit()
        # make request with forbidden intervall
        response = self.client.get(
            f"/api/embeddingIntervalData/{self.assocData_intervals_unowned.id}/",
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
                self.owned_collection,
                self.owned_bedfile,
                self.owned_intervals,
                self.assocData_owned,
            ]
        )
        db.session.commit()
        # make request
        response = self.client.get(
            f"/api/embeddingIntervalData/{self.assocData_owned.id}/",
            headers=token_headers,
            content_type="application/json",
        )
        data = json.loads(gzip.decompress(response.data))
        expected = {
            "embedding": {
                "data": self.test_data.flatten().tolist(),
                "shape": list(self.test_data.shape),
                "dtype": "float32",
            }
        }
        self.assertEqual(data, expected)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
