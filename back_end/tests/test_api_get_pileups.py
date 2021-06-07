import os
import pdb
import unittest
import pandas as pd
import numpy as np
from test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
import sys

sys.path.append("./")
from app import db
from app.models import Dataset, Intervals, AverageIntervalData


class TestGetAverageIntervalDataData(LoginTestCase, TempDirTestCase):
    """Test to check whether retrieving of averageIntervalData data
    works."""

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
        dataset1 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="cooler",
            user_id=5,
        )
        dataset2 = Dataset(
            dataset_name="test2",
            file_path="/test/path/2",
            filetype="bedfile",
            user_id=1,
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=2,
            file_path="test_path_1.bedd2db",
            windowsize=200000,
        )
        averageIntervalData = AverageIntervalData(
            name="testAverageIntervalData1",
            binsize=10000,
            file_path="testPath1",
            dataset_id=1,
            intervals_id=1,
            value_type="ICCF",
        )
        db.session.add_all([dataset1, dataset2, intervals1, averageIntervalData])
        db.session.commit()
        # make request for forbidden cooler
        response = self.client.get(
            "/api/averageIntervalData/1/",
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
        dataset1 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="cooler",
            user_id=1,
        )
        dataset2 = Dataset(
            dataset_name="test2",
            file_path="/test/path/2",
            filetype="bedfile",
            user_id=5,
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=2,
            file_path="test_path_1.bedd2db",
            windowsize=200000,
        )
        averageIntervalData = AverageIntervalData(
            name="testAverageIntervalData1",
            binsize=10000,
            file_path="testPath1",
            dataset_id=1,
            intervals_id=1,
            value_type="ICCF",
        )
        db.session.add_all([dataset1, dataset2, intervals1, averageIntervalData])
        db.session.commit()
        # make request with forbidden intervall
        response = self.client.get(
            "/api/averageIntervalData/1/",
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
        # create datafile
        test_data_return = {
            "data": [1.66, 2.2, 3.8, 4.5],
            "shape": [1, 4],
            "dtype": "float32",
        }
        test_data = np.array([[1.66, 2.2, 3.8, 4.5]])
        data_path = os.path.join(TempDirTestCase.TEMP_PATH, "test.npy")
        np.save(data_path, test_data)

        # add data
        dataset1 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="cooler",
            user_id=1,
        )
        dataset2 = Dataset(
            dataset_name="test2",
            file_path="/test/path/2",
            filetype="bedfile",
            user_id=1,
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=2,
            file_path="test_path_1.bedd2db",
            windowsize=200000,
        )
        averageIntervalData = AverageIntervalData(
            name="testAverageIntervalData1",
            binsize=10000,
            file_path=data_path,
            dataset_id=1,
            intervals_id=1,
            value_type="ICCF",
        )
        db.session.add_all([dataset1, dataset2, intervals1, averageIntervalData])
        db.session.commit()
        # make request
        response = self.client.get(
            "/api/averageIntervalData/1/",
            headers=token_headers,
            content_type="application/json",
        )
        expected = test_data_return
        self.assertEqual(response.json, expected)

    def test_correct_data_returned_with_nan(self):
        """Correct data is returned from an owned averageIntervalData
        that contains nan"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # create datafile
        test_data_return = {
            "data": [1.66, 2.2, 3.8, 4.5, None],
            "shape": [1, 5],
            "dtype": "float32",
        }

        test_data = np.array([[1.66, 2.2, 3.8, 4.5, np.nan]])
        data_path = os.path.join(TempDirTestCase.TEMP_PATH, "test.npy")
        np.save(data_path, test_data)

        # add data
        dataset1 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="cooler",
            user_id=1,
        )
        dataset2 = Dataset(
            dataset_name="test2",
            file_path="/test/path/2",
            filetype="bedfile",
            user_id=1,
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=2,
            file_path="test_path_1.bedd2db",
            windowsize=200000,
        )
        averageIntervalData = AverageIntervalData(
            name="testAverageIntervalData1",
            binsize=10000,
            file_path=data_path,
            dataset_id=1,
            intervals_id=1,
            value_type="ICCF",
        )
        db.session.add_all([dataset1, dataset2, intervals1, averageIntervalData])
        db.session.commit()
        # make request
        response = self.client.get(
            "/api/averageIntervalData/1/",
            headers=token_headers,
            content_type="application/json",
        )
        expected = test_data_return
        self.assertEqual(response.json, expected)

    def test_correct_data_returned_with_inf(self):
        """Correct data is returned from an owned averageIntervalData
        that contains nan"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # create datafile
        test_data_return = {
            "data": [1.66, 2.2, 3.8, 4.5, None],
            "shape": [1, 5],
            "dtype": "float32",
        }

        test_data = np.array([[1.66, 2.2, 3.8, 4.5, np.inf]])
        data_path = os.path.join(TempDirTestCase.TEMP_PATH, "test.npy")
        np.save(data_path, test_data)

        # add data
        dataset1 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="cooler",
            user_id=1,
        )
        dataset2 = Dataset(
            dataset_name="test2",
            file_path="/test/path/2",
            filetype="bedfile",
            user_id=1,
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=2,
            file_path="test_path_1.bedd2db",
            windowsize=200000,
        )
        averageIntervalData = AverageIntervalData(
            name="testAverageIntervalData1",
            binsize=10000,
            file_path=data_path,
            dataset_id=1,
            intervals_id=1,
            value_type="ICCF",
        )
        db.session.add_all([dataset1, dataset2, intervals1, averageIntervalData])
        db.session.commit()
        # make request
        response = self.client.get(
            "/api/averageIntervalData/1/",
            headers=token_headers,
            content_type="application/json",
        )
        expected = test_data_return
        self.assertEqual(response.json, expected)

    def test_public_unowned_data_returned(self):
        """Test whether public, unowned data is returned correctly."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # create datafile
        test_data_back = {
            "data": [1.66, 2.2, 3.8, 4.5],
            "shape": [1, 4],
            "dtype": "float32",
        }

        test_data = np.array([[1.66, 2.2, 3.8, 4.5]])
        data_path = os.path.join(TempDirTestCase.TEMP_PATH, "test.npy")
        np.save(data_path, test_data)
        # add data
        dataset1 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="cooler",
            public=True,
            user_id=2,
        )
        dataset2 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="bedfile",
            public=True,
            user_id=2,
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=2,
            file_path="test_path_1.bedd2db",
            windowsize=200000,
        )
        averageIntervalData = AverageIntervalData(
            name="testAverageIntervalData1",
            binsize=10000,
            file_path=data_path,
            dataset_id=1,
            intervals_id=1,
            value_type="ICCF",
        )
        db.session.add_all([dataset1, dataset2, intervals1, averageIntervalData])
        db.session.commit()
        # make request
        response = self.client.get(
            "/api/averageIntervalData/1/",
            headers=token_headers,
            content_type="application/json",
        )
        expected = test_data_back
        self.assertEqual(response.json, expected)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
