 """Test to check whether retrieving of averageIntervalData data works."""
import os
import unittest
import numpy as np
from hicognition.test_helpers import LoginTestCase, TempDirTestCase
# add path to import app
# import sys
# sys.path.append("./")
from app import db
from app.models import Dataset, Intervals, AverageIntervalData


class TestGetAverageIntervalData(LoginTestCase, TempDirTestCase):
    """Test to check whether retrieving of averageIntervalData data
    works."""

    def setUp(self):
        super().setUp()
        # add owned cooler
        self.owned_cooler = Dataset(
            id=1,
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="cooler",
            user_id=1,
        )
        # add unowned cooler
        self.unowned_cooler = Dataset(
            id=2,
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="cooler",
            user_id=2,
        )
        # add owned bedfile
        self.owned_bedfile = Dataset(
            id=3,
            dataset_name="test2",
            file_path="/test/path/2",
            filetype="bedfile",
            user_id=1,
        )
        # add unowned bedfile
        self.unowned_bedfile = Dataset(
            id=4,
            dataset_name="test2",
            file_path="/test/path/2",
            filetype="bedfile",
            user_id=2,
        )
        # add unowned, public cooler
        self.unowned_public_cooler = Dataset(
            id=5,
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="cooler",
            user_id=2,
            public=True,
        )
        # add unowned, public bedfile
        self.unowned_public_bedfile = Dataset(
            id=6,
            dataset_name="test2",
            file_path="/test/path/2",
            filetype="bedfile",
            user_id=2,
            public=True,
        )
        # add intervals for owned bedfile
        self.owned_intervals = Intervals(
            id=1,
            name="testRegion1",
            dataset_id=self.owned_bedfile.id,
            windowsize=200000,
        )
        # add intervals for unowned bedfile
        self.unowned_intervals = Intervals(
            id=2,
            name="testRegion1",
            dataset_id=self.unowned_bedfile.id,
            windowsize=200000,
        )
        # add intervals for unowned, public bedfile
        self.unowned_public_intervals = Intervals(
            id=3,
            name="testRegion1",
            dataset_id=self.unowned_public_bedfile.id,
            windowsize=200000,
        )
        # add averageIntervalData with unowned cooler
        self.avgData_cooler_unowned = AverageIntervalData(
            id=1,
            name="testAverageIntervalData1",
            binsize=10000,
            file_path="testPath1",
            dataset_id=self.unowned_cooler.id,
            intervals_id=self.owned_intervals.id,
            value_type="ICCF",
        )
        # add averageIntervalData with unowned intervals
        self.avgData_intervals_unowned = AverageIntervalData(
            id=2,
            name="testAverageIntervalData1",
            binsize=10000,
            file_path="testPath1",
            dataset_id=self.owned_cooler.id,
            intervals_id=self.unowned_intervals.id,
            value_type="ICCF",
        )
        # add averageIntervalData with owned intervals and cooler and associated data
        self.test_data = np.array([[1.66, 2.2, 3.8, 4.5]])
        data_path = os.path.join(TempDirTestCase.TEMP_PATH, "test.npy")
        np.save(data_path, self.test_data)
        self.avgData_owned = AverageIntervalData(
            id=3,
            name="testAverageIntervalData1",
            binsize=10000,
            file_path=data_path,
            dataset_id=1,
            intervals_id=1,
            value_type="ICCF",
        )
        # add averageIntervalData with owned intervals and cooler and associated data containing nans
        self.test_data_w_nans = np.array([[1.66, 2.2, 3.8, 4.5, np.nan]])
        data_path_w_nans = os.path.join(TempDirTestCase.TEMP_PATH, "test1.npy")
        np.save(data_path_w_nans, self.test_data_w_nans)
        self.avgData_owned_w_nans = AverageIntervalData(
            id=4,
            name="testAverageIntervalData1",
            binsize=10000,
            file_path=data_path_w_nans,
            dataset_id=1,
            intervals_id=1,
            value_type="ICCF",
        )
        # add averageIntervalData with owned intervals and cooler and associated data containing inf
        self.test_data_w_inf = np.array([[1.66, 2.2, 3.8, 4.5, np.inf]])
        data_path_w_inf = os.path.join(TempDirTestCase.TEMP_PATH, "test2.npy")
        np.save(data_path_w_inf, self.test_data_w_inf)
        self.avgData_owned_w_inf = AverageIntervalData(
            id=5,
            name="testAverageIntervalData1",
            binsize=10000,
            file_path=data_path_w_inf,
            dataset_id=1,
            intervals_id=1,
            value_type="ICCF",
        )
        # add averageIntervalData with public intervals and cooler and associated data
        self.avgData_unowned_public = AverageIntervalData(
            id=6,
            name="testAverageIntervalData1",
            binsize=10000,
            file_path=data_path,
            dataset_id=self.unowned_public_cooler.id,
            intervals_id=self.unowned_public_intervals.id,
            value_type="ICCF",
        )

    def test_no_auth(self):
        """No authentication provided, response should be 401"""
        # protected route
        response = self.client.get(
            "/api/averageIntervalData/1/", content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

    def test_averageIntervalData_does_not_exist(self):
        """Test 404 is returned if averageIntervalData does not exist."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # make request
        response = self.client.get(
            "/api/averageIntervalData/500/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_cooler_not_owned(self):
        """Cooler dataset underlying averageIntervalData is not owned"""
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
                self.avgData_cooler_unowned,
            ]
        )
        db.session.commit()
        # make request for forbidden cooler
        response = self.client.get(
            f"/api/averageIntervalData/{self.avgData_cooler_unowned.id}/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_intervals_not_owned(self):
        """Intervals dataset underlying averageIntervalData is not owned"""
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
                self.avgData_intervals_unowned,
            ]
        )
        db.session.commit()
        # make request with forbidden intervall
        response = self.client.get(
            f"/api/averageIntervalData/{self.avgData_intervals_unowned.id}/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_correct_data_returned(self):
        """Correct data is returned from an owned averageIntervalData"""
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
                self.avgData_owned,
            ]
        )
        db.session.commit()
        # make request
        response = self.client.get(
            f"/api/averageIntervalData/{self.avgData_owned.id}/",
            headers=token_headers,
            content_type="application/json",
        )
        expected = {
            "data": self.test_data.flatten().tolist(),
            "shape": list(self.test_data.shape),
            "dtype": "float32",
        }
        self.assertEqual(response.json, expected)

    def test_correct_data_returned_with_nan(self):
        """Correct data is returned from an owned averageIntervalData
        that contains nan"""
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
                self.avgData_owned_w_nans,
            ]
        )
        db.session.commit()
        # make request
        response = self.client.get(
            f"/api/averageIntervalData/{self.avgData_owned_w_nans.id}/",
            headers=token_headers,
            content_type="application/json",
        )
        expected = {
            "data": [
                i if not np.isnan(i) else None for i in self.test_data_w_nans.flatten()
            ],
            "shape": list(self.test_data_w_nans.shape),
            "dtype": "float32",
        }
        self.assertEqual(response.json, expected)

    def test_correct_data_returned_with_inf(self):
        """Correct data is returned from an owned averageIntervalData
        that contains nan"""
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
                self.avgData_owned_w_inf,
            ]
        )
        db.session.commit()
        # make request
        response = self.client.get(
            f"/api/averageIntervalData/{self.avgData_owned_w_inf.id}/",
            headers=token_headers,
            content_type="application/json",
        )
        expected = {
            "data": [
                i if not np.isinf(i) else None for i in self.test_data_w_inf.flatten()
            ],
            "shape": list(self.test_data_w_inf.shape),
            "dtype": "float32",
        }
        self.assertEqual(response.json, expected)

    def test_public_unowned_data_returned(self):
        """Test whether public, unowned data is returned correctly."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        db.session.add_all(
            [
                self.unowned_public_cooler,
                self.unowned_public_bedfile,
                self.unowned_public_intervals,
                self.avgData_unowned_public,
            ]
        )
        db.session.commit()
        db.session.commit()
        # make request
        response = self.client.get(
            f"/api/averageIntervalData/{self.avgData_unowned_public.id}/",
            headers=token_headers,
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
