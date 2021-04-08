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
from app.models import Dataset, Intervals, IndividualIntervalData


class TestGetIndividualIntervalDatas(LoginTestCase):
    """Tests for /api/individualIntervalData route to list
    individualIntervalData."""

    def test_no_auth(self):
        """No authentication provided, response should be 401"""
        # protected route
        response = self.client.get(
            "/api/individualIntervalData/?dataset_id=1&intervals_id=2",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

    def test_bigwig_dataset_does_not_exist(self):
        """Test whether 404 if bigwig dataset does not exist"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        dataset1 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="bigwig",
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
        individualIntervalData = IndividualIntervalData(
            name="testIndividualIntervalData1",
            binsize=10000,
            file_path="testPath1",
            file_path_small="testPath1_small",
            dataset_id=1,
            intervals_id=1,
        )
        db.session.add_all([dataset1, dataset2, intervals1, individualIntervalData])
        db.session.commit()
        # make query for non-existent bigwig
        response = self.client.get(
            "/api/individualIntervalData/?dataset_id=500&intervals_id=1",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_intervals_does_not_exist(self):
        """Test whether 404 if intervals dataset does not exist"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        dataset1 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="bigwig",
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
        individualIntervalData = IndividualIntervalData(
            name="testIndividualIntervalData1",
            binsize=10000,
            file_path="testPath1",
            file_path_small="testPath1_small",
            dataset_id=1,
            intervals_id=1,
        )
        db.session.add_all([dataset1, dataset2, intervals1, individualIntervalData])
        db.session.commit()
        # make query for non-existent intervals
        response = self.client.get(
            "/api/individualIntervalData/?dataset_id=1&intervals_id=500",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_no_parameters_provided(self):
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        dataset1 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="bigwig",
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
        individualIntervalData = IndividualIntervalData(
            name="testIndividualIntervalData1",
            binsize=10000,
            file_path="testPath1",
            file_path_small="testPath1_small",
            dataset_id=1,
            intervals_id=1,
        )
        db.session.add_all([dataset1, dataset2, intervals1, individualIntervalData])
        db.session.commit()
        # make query with no parameters
        response = self.client.get(
            "/api/individualIntervalData/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_no_bigwig_provided(self):
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        dataset1 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="bigwig",
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
        individualIntervalData = IndividualIntervalData(
            name="testIndividualIntervalData1",
            binsize=10000,
            file_path="testPath1",
            file_path_small="testPath1_small",
            dataset_id=1,
            intervals_id=1,
        )
        db.session.add_all([dataset1, dataset2, intervals1, individualIntervalData])
        db.session.commit()
        # make query with no bigwig provided
        response = self.client.get(
            "/api/individualIntervalData/?intervals_id=1",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_no_intervals_provided(self):
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        dataset1 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="bigwig",
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
        individualIntervalData = IndividualIntervalData(
            name="testIndividualIntervalData1",
            binsize=10000,
            file_path="testPath1",
            file_path_small="testPath1_small",
            dataset_id=1,
            intervals_id=1,
        )
        db.session.add_all([dataset1, dataset2, intervals1, individualIntervalData])
        db.session.commit()
        # make query with no intervall provided
        response = self.client.get(
            "/api/individualIntervalData/?dataset_id=1",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_forbidden_bigwig_not_owned(self):
        """Tests whether 403 response is sent if
        bigwig file is not owned by user in token."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token2 = self.add_and_authenticate("test2", "fdsa")
        # create token header
        token_headers = self.get_token_header(token)
        token_headers2 = self.get_token_header(token2)
        # add data
        dataset1 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="bigwig",
            user_id=2,
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
        individualIntervalData = IndividualIntervalData(
            name="testIndividualIntervalData1",
            binsize=10000,
            file_path="testPath1",
            file_path_small="testPath1_small",
            dataset_id=1,
            intervals_id=1,
        )
        db.session.add_all([dataset1, dataset2, intervals1, individualIntervalData])
        db.session.commit()
        # make query with forbidden bigwig
        response = self.client.get(
            "/api/individualIntervalData/?dataset_id=1&intervals_id=1",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_forbidden_intervals_not_owned(self):
        """Test whether 403 is sent if intervals are not owned."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token2 = self.add_and_authenticate("test2", "fdsa")
        # create token header
        token_headers = self.get_token_header(token)
        token_headers2 = self.get_token_header(token2)
        # add data
        dataset1 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="bigwig",
            user_id=1,
        )
        dataset2 = Dataset(
            dataset_name="test2",
            file_path="/test/path/2",
            filetype="bedfile",
            user_id=2,
        )
        dataset3 = Dataset(
            dataset_name="test3",
            file_path="/test/path/3",
            filetype="bedfile",
            user_id=1,
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=2,
            file_path="test_path_1.bedd2db",
            windowsize=200000,
        )
        intervals2 = Intervals(
            name="testRegion2",
            dataset_id=3,
            file_path="test_path_2.bedd2db",
            windowsize=200000,
        )
        individualIntervalData = IndividualIntervalData(
            name="testIndividualIntervalData1",
            binsize=10000,
            file_path="testPath1",
            file_path_small="testPath1_small",
            dataset_id=1,
            intervals_id=1,
        )
        db.session.add_all(
            [
                dataset1,
                dataset2,
                dataset3,
                intervals1,
                intervals2,
                individualIntervalData,
            ]
        )
        db.session.commit()
        # make query with forbidden interval
        response = self.client.get(
            "/api/individualIntervalData/?dataset_id=1&intervals_id=1",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_get_individualIntervalData_allowed_for_public_unowned(self):
        """Tests whether listing individualIntervalData is allowed for an unowned but public dataset."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        dataset1 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="bigwig",
            public=True,
            user_id=2,
        )
        dataset2 = Dataset(
            dataset_name="test2",
            file_path="/test/path/2",
            filetype="bigwig",
            public=True,
            user_id=2,
        )
        dataset3 = Dataset(
            dataset_name="test3",
            file_path="/test/path/3",
            filetype="bedfile",
            public=True,
            user_id=2,
        )
        dataset4 = Dataset(
            dataset_name="test4",
            file_path="/test/path/4",
            filetype="bedfile",
            public=True,
            user_id=2,
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=3,
            file_path="test_path_1.bedd2db",
            windowsize=200000,
        )
        intervals2 = Intervals(
            name="testRegion2",
            dataset_id=4,
            file_path="test_path_2.bedd2db",
            windowsize=200000,
        )
        individualIntervalData1 = IndividualIntervalData(
            name="testIndividualIntervalData1",
            binsize=10000,
            file_path="testPath1",
            file_path_small="testPath1_small",
            dataset_id=1,
            intervals_id=1,
        )
        individualIntervalData2 = IndividualIntervalData(
            name="testIndividualIntervalData2",
            binsize=10000,
            file_path="testPath2",
            file_path_small="testPath2_small",
            dataset_id=1,
            intervals_id=2,
        )
        individualIntervalData3 = IndividualIntervalData(
            name="testIndividualIntervalData3",
            binsize=10000,
            file_path="testPath3",
            file_path_small="testPath3_small",
            dataset_id=2,
            intervals_id=1,
        )
        individualIntervalData4 = IndividualIntervalData(
            name="testIndividualIntervalData4",
            binsize=10000,
            file_path="testPath4",
            file_path_small="testPath4_small",
            dataset_id=2,
            intervals_id=2,
        )
        db.session.add_all(
            [
                dataset1,
                dataset2,
                dataset3,
                dataset4,
                intervals1,
                intervals2,
                individualIntervalData1,
                individualIntervalData2,
                individualIntervalData3,
                individualIntervalData4,
            ]
        )
        db.session.commit()
        # make query 1
        response = self.client.get(
            "/api/individualIntervalData/?dataset_id=1&intervals_id=1",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]["id"], 1)
        # make query 2
        response = self.client.get(
            "/api/individualIntervalData/?dataset_id=1&intervals_id=2",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]["id"], 2)


class TestGetIndividualIntervalDataData(LoginTestCase, TempDirTestCase):
    """Test to check whether retrieving of individualIntervalData data
    works."""

    def test_no_auth(self):
        """No authentication provided, response should be 401"""
        # protected route
        response = self.client.get(
            "/api/individualIntervalData/1/", content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

    def test_individualIntervalData_does_not_exist(self):
        """Test 404 is returned if individualIntervalData does not exist."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # make request
        response = self.client.get(
            "/api/individualIntervalData/500/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_bigwig_not_owned(self):
        """Bigwig dataset underlying individualIntervalData is not owned"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        dataset1 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="bigwig",
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
        individualIntervalData = IndividualIntervalData(
            name="testIndividualIntervalData1",
            binsize=10000,
            file_path="testPath1",
            file_path_small="testPath1_small",
            dataset_id=1,
            intervals_id=1,
        )
        db.session.add_all([dataset1, dataset2, intervals1, individualIntervalData])
        db.session.commit()
        # make request
        response = self.client.get(
            "/api/individualIntervalData/1/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_intervals_not_owned(self):
        """Intervals dataset underlying individualIntervalData is not owned"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        dataset1 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="bigwig",
            user_id=1,
        )
        dataset2 = Dataset(
            dataset_name="test2",
            file_path="/test/path/1",
            filetype="bedfile",
            user_id=5,
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=2,
            file_path="test_path_1.bedd2db",
            windowsize=200000,
        )
        individualIntervalData = IndividualIntervalData(
            name="testIndividualIntervalData1",
            binsize=10000,
            file_path="testPath1",
            file_path_small="testPath1_small",
            dataset_id=1,
            intervals_id=1,
        )
        db.session.add_all([dataset1, dataset2, intervals1, individualIntervalData])
        db.session.commit()
        # make request for bigwig with forbidden interval
        response = self.client.get(
            "/api/individualIntervalData/1/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)


    def test_correct_data_returned(self):
        """Correct data is returned from an owned individualIntervalData"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # create datafile
        arr = np.array([[1.66, 2.2, 3.8, 4.5]])
        data_path = os.path.join(TempDirTestCase.TEMP_PATH, "test.npy")
        np.save(data_path, arr)

        # add data
        dataset1 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="bigwig",
            user_id=1,
        )
        dataset2 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="bedfile",
            user_id=1,
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=2,
            file_path="test_path_1.bedd2db",
            windowsize=200000,
        )
        individualIntervalData = IndividualIntervalData(
            name="testIndividualIntervalData1",
            binsize=10000,
            file_path="data_path_big",
            file_path_small=data_path,
            dataset_id=1,
            intervals_id=1,
        )
        db.session.add_all([dataset1, dataset2, intervals1, individualIntervalData])
        db.session.commit()
        # make request
        response = self.client.get(
            "/api/individualIntervalData/1/",
            headers=token_headers,
            content_type="application/json",
        )
        # compare by hand
        self.assertTrue(np.all(np.isclose(arr, response.json["data"])))
        self.assertEqual("float32", response.json["dtype"])
        self.assertTrue(np.all(np.isclose([1, 4], response.json["shape"])))

    def test_public_unowned_data_returned(self):
        """Test whether public, unowned data is returned correctly."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # create datafile
        arr = np.array([[1.66, 2.2, 3.8, 4.5]])
        data_path = os.path.join(TempDirTestCase.TEMP_PATH, "test.npy")
        np.save(data_path, arr)

        # add data
        dataset1 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="bigwig",
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
        individualIntervalData = IndividualIntervalData(
            name="testIndividualIntervalData1",
            binsize=10000,
            file_path="data_path_big",
            file_path_small=data_path,
            dataset_id=1,
            intervals_id=1,
        )
        db.session.add_all([dataset1, dataset2, intervals1, individualIntervalData])
        db.session.commit()
        # make request
        response = self.client.get(
            "/api/individualIntervalData/1/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertTrue(np.all(np.isclose(arr, response.json["data"])))
        self.assertEqual("float32", response.json["dtype"])
        self.assertTrue(np.all(np.isclose([1, 4], response.json["shape"])))


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
