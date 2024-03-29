"""Tests for get route of association interval data."""
import os
import unittest
from unittest.mock import patch
import numpy as np
from tests.test_utils.test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
# import sys
# sys.path.append("./")
from app import db
from app.models import Collection, Dataset, Intervals, AssociationIntervalData


class TestGetAssociationIntervalData(LoginTestCase, TempDirTestCase):
    """Tests for get route of association interval data."""

    def setUp(self):
        super().setUp()
        # add owned collection
        self.owned_collection = Collection(id=1, user_id=1)
        # add unowned collection
        self.unowned_collection = Collection(id=2, user_id=2)
        # add owned bedfile
        self.owned_bedfile = self.create_dataset(id=3, dataset_name="test3", filetype="bedfile", user_id=1)
        # add unowned bedfile
        self.unowned_bedfile = self.create_dataset(id=4, dataset_name="test4", filetype="bedfile", user_id=2)
        # add intervals for owned bedfile
        self.owned_intervals = Intervals(
            id=1,dataset_id=self.owned_bedfile.id, windowsize=200000
        )
        # add intervals for unowned bedfile
        self.unowned_intervals = Intervals(
            id=2, dataset_id=self.unowned_bedfile.id, windowsize=200000
        )
        # add associationIntervalData with unowned collection
        self.assoc_data_collection_unowned = AssociationIntervalData(
            id=1,
            binsize=10000,
            collection_id=self.unowned_collection.id,
            intervals_id=self.owned_intervals.id,
        )
        # add averageIntervalData with unowned intervals
        self.assoc_data_intervals_unowned = AssociationIntervalData(
            id=2,
            binsize=10000,
            collection_id=self.owned_collection.id,
            intervals_id=self.unowned_intervals.id,
        )
        # add associationIntervalData with owned intervals and collection and associated data
        self.test_data = np.array([[1.66, 2.2, 3.8, 4.5]])
        data_path = os.path.join(TempDirTestCase.TEMP_PATH, "test.npy")
        np.save(data_path, self.test_data)
        self.assoc_data_owned = AssociationIntervalData(
            id=3, binsize=10000, file_path=data_path, collection_id=1, intervals_id=1
        )

    def test_no_auth(self):
        """No authentication provided, response should be 401"""
        # protected route
        response = self.client.get(
            "/api/associationIntervalData/1/", content_type="application/json"
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
                "/api/associationIntervalData/1/", content_type="application/json"
            )
            self.assertEqual(response.status_code, 404)

    def test_association_interval_data_does_not_exist(self):
        """Test 404 is returned if associationIntervalData does not exist."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # make request
        response = self.client.get(
            "/api/associationIntervalData/500/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_collection_not_owned(self):
        """Collection underlying associationIntervalData is not owned"""
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
            f"/api/associationIntervalData/{self.assoc_data_collection_unowned.id}/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_intervals_not_owned(self):
        """Intervals dataset underlying associationIntervalData are not owned"""
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
        # make request with forbidden interval
        response = self.client.get(
            f"/api/associationIntervalData/{self.assoc_data_intervals_unowned.id}/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_correct_data_returned(self):
        """Correct data is returned from an owned associationIntervalData"""
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
            f"/api/associationIntervalData/{self.assoc_data_owned.id}/",
            headers=token_headers,
            content_type="application/json",
        )
        expected = {
            "data": self.test_data.flatten().tolist(),
            "shape": list(self.test_data.shape),
            "dtype": "float32",
        }
        self.assertEqual(response.json, expected)

    def test_correct_data_returned_for_showcase_user(self):
        """Correct data is returned from an owned associationIntervalData"""
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
                f"/api/associationIntervalData/{self.assoc_data_owned.id}/",
                content_type="application/json",
            )
            expected = {
                "data": self.test_data.flatten().tolist(),
                "shape": list(self.test_data.shape),
                "dtype": "float32",
            }
            self.assertEqual(response.json, expected)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
