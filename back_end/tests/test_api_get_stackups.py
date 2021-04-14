import os
import pandas as pd
import unittest
import numpy as np
from test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
import sys

sys.path.append("./")
from app import db
from app.models import Dataset, Intervals, IndividualIntervalData, BedFileMetadata


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
        test_data_return = {
            "data": [1.66, 2.2, 3.8, 4.5],
            "shape": [1, 4],
            "dtype": "float32",
        }
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
        self.assertEqual(response.json, test_data_return)

    def test_correct_data_returned_w_nan(self):
        """Correct data is returned from an owned individualIntervalData that contains nan"""
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
        arr = np.array([[1.66, 2.2, 3.8, 4.5, np.nan]])
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
        self.assertEqual(response.json, test_data_return)

    def test_correct_data_returned_w_inf(self):
        """Correct data is returned from an owned individualIntervalData that contains nan"""
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
        arr = np.array([[1.66, 2.2, 3.8, 4.5, np.inf]])
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
        self.assertEqual(response.json, test_data_return)

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


class TestGetStackupMetadata(LoginTestCase, TempDirTestCase):
    """Tests for /individualIntervalData/<stackup_id>/metadatasmall"""

    def test_no_auth(self):
        """No authentication provided, response should be 401"""
        # protected route
        response = self.client.get(
            "/api/individualIntervalData/1/metadatasmall",
            content_type="application/json",
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
            "/api/individualIntervalData/500/metadatasmall",
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
            "/api/individualIntervalData/1/metadatasmall",
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
            "/api/individualIntervalData/1/metadatasmall",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_empty_response_no_metadata(self):
        """Tests whether empty response is returned when there are no associated metadata"""
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
            file_path_small="test_path",
            dataset_id=1,
            intervals_id=1,
        )
        db.session.add_all([dataset1, dataset2, intervals1, individualIntervalData])
        db.session.commit()
        # make request
        response = self.client.get(
            "/api/individualIntervalData/1/metadatasmall",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.json, {})

    def test_good_single_metadata_entry_is_returned_correctly(self):
        """Tests whether single associated metadata entry to
        small stackup file is returned correctly, meaning the
        corresponding indices are returned."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers2 = self.get_token_header(token)
        # generate mock datasets in temp-directory
        metadata_file_path = os.path.join(TempDirTestCase.TEMP_PATH, "test.csv")
        metadata_df = pd.DataFrame(
            {"id": [0, 1, 2, 3, 4, 5], "start": [0] * 6, "end": [10] * 6}
        )
        metadata_df.to_csv(metadata_file_path, index=False)
        # generate mock index file for stackup susbet
        indices = np.array([0, 2])
        index_file = os.path.join(TempDirTestCase.TEMP_PATH, "indices.npy")
        np.save(index_file, indices)
        # add data
        dataset1 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="bedfile",
            user_id=1,
        )
        dataset2 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="bigwig",
            user_id=1,
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=1,
            file_path="intervals_test_path",
            windowsize=200000,
        )
        metadata1 = BedFileMetadata(
            file_path=metadata_file_path,
            metadata_fields='["id", "start"]',
            dataset_id=1,
        )
        individualIntervalData = IndividualIntervalData(
            name="testIndividualIntervalData1",
            binsize=10000,
            file_path="data_path_big",
            file_path_small="test_path",
            file_path_indices_small=index_file,
            dataset_id=2,
            intervals_id=1,
        )
        db.session.add_all(
            [dataset1, dataset2, intervals1, metadata1, individualIntervalData]
        )
        db.session.commit()
        # make apicall
        response = self.client.get(
            "/api/individualIntervalData/1/metadatasmall",
            headers=token_headers2,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            metadata_df.drop("end", axis="columns")
            .iloc[[0, 2], :]
            .to_dict(orient="list"),
        )

    def test_entries_with_no_fields_specified_are_not_returned(self):
        """Tests whether associated metadata fiels with no field names
        specified are not returned"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers2 = self.get_token_header(token)
        # generate mock datasets in temp-directory
        metadata_file_path = os.path.join(TempDirTestCase.TEMP_PATH, "test.csv")
        metadata_df = pd.DataFrame(
            {"id": [0, 1, 2, 3, 4, 5], "start": [0] * 6, "end": [10] * 6}
        )
        metadata_df.to_csv(metadata_file_path, index=False)
        metadata_file_path_2 = os.path.join(TempDirTestCase.TEMP_PATH, "test2.csv")
        metadata_df_2 = pd.DataFrame({"end": [10] * 6})
        metadata_df_2.to_csv(metadata_file_path_2, index=False)
        # generate mock index file for stackup susbet
        indices = np.array([0, 2])
        index_file = os.path.join(TempDirTestCase.TEMP_PATH, "indices.npy")
        np.save(index_file, indices)
        # add data
        dataset1 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="bedfile",
            user_id=1,
        )
        dataset2 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="bigwig",
            user_id=1,
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=1,
            file_path="intervals_test_path",
            windowsize=200000,
        )
        metadata1 = BedFileMetadata(
            file_path=metadata_file_path,
            metadata_fields='["id", "start"]',
            dataset_id=1,
        )
        metadata2 = BedFileMetadata(file_path=metadata_file_path_2, dataset_id=1)
        individualIntervalData = IndividualIntervalData(
            name="testIndividualIntervalData1",
            binsize=10000,
            file_path="data_path_big",
            file_path_small="test_path",
            file_path_indices_small=index_file,
            dataset_id=2,
            intervals_id=1,
        )
        db.session.add_all(
            [
                dataset1,
                dataset2,
                intervals1,
                metadata1,
                metadata2,
                individualIntervalData,
            ]
        )
        db.session.commit()
        # make apicall
        response = self.client.get(
            "/api/individualIntervalData/1/metadatasmall",
            headers=token_headers2,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            metadata_df.drop("end", axis="columns")
            .iloc[[0, 2], :]
            .to_dict(orient="list"),
        )

    def test_metadata_entries_with_overlapping_fieldname_are_returned_correctly(self):
        """Tests whether multiple associated metadata entries to
        interval file with overlapping fieldnames returned the newest field (by larger id value)"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers2 = self.get_token_header(token)
        # generate mock datasets in temp-directory
        metadata_file_path = os.path.join(TempDirTestCase.TEMP_PATH, "test.csv")
        metadata_df = pd.DataFrame(
            {"id": [0, 1, 2, 3, 4, 5], "start": [0] * 6, "end": [10] * 6}
        )
        metadata_df.to_csv(metadata_file_path, index=False)
        metadata_file_path_2 = os.path.join(TempDirTestCase.TEMP_PATH, "test2.csv")
        metadata_df_2 = pd.DataFrame({"end": [12] * 6})
        metadata_df_2.to_csv(metadata_file_path_2, index=False)
        # generate mock index file for stackup susbet
        indices = np.array([0, 2])
        index_file = os.path.join(TempDirTestCase.TEMP_PATH, "indices.npy")
        np.save(index_file, indices)
        # add data
        dataset1 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="bedfile",
            user_id=1,
        )
        dataset2 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="bigwig",
            user_id=1,
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=1,
            file_path="intervals_test_path",
            windowsize=200000,
        )
        metadata1 = BedFileMetadata(
            file_path=metadata_file_path,
            metadata_fields='["id", "start"]',
            dataset_id=1,
        )
        metadata2 = BedFileMetadata(
            id=2,
            file_path=metadata_file_path,
            metadata_fields='["id", "start", "end"]',
            dataset_id=1,
        )
        individualIntervalData = IndividualIntervalData(
            name="testIndividualIntervalData1",
            binsize=10000,
            file_path="data_path_big",
            file_path_small="test_path",
            file_path_indices_small=index_file,
            dataset_id=2,
            intervals_id=1,
        )
        db.session.add_all(
            [
                dataset1,
                dataset2,
                intervals1,
                metadata1,
                metadata2,
                individualIntervalData,
            ]
        )
        db.session.commit()
        # make apicall
        response = self.client.get(
            "/api/individualIntervalData/1/metadatasmall",
            headers=token_headers2,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            metadata_df.iloc[[0, 2], :].to_dict(orient="list"),
        )


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
