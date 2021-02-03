import os
import pdb
import unittest
import pandas as pd
from test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
import sys

sys.path.append("./")
from app import db
from app.models import Dataset, Intervals, AverageIntervalData


class TestGetAverageIntervalDatas(LoginTestCase):
    """Tests for /api/averageIntervalData route to list
    averageIntervalData."""

    def test_no_auth(self):
        """No authentication provided, response should be 401"""
        # protected route
        response = self.client.get(
            "/api/averageIntervalData/?cooler_id=1&intervals_id=2",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

    def test_cooler_dataset_does_not_exist(self):
        """Test whether 404 if cooler dataset does not exist"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        dataset1 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            higlass_uuid="asdf1234",
            filetype="cooler",
            user_id=1,
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            higlass_uuid="testHiglass1",
            windowsize=200000,
        )
        averageIntervalData = AverageIntervalData(
            name="testAverageIntervalData1",
            binsize=10000,
            file_path="testPath1",
            cooler_id=1,
            intervals_id=1,
            value_type="ICCF",
        )
        db.session.add_all([dataset1, intervals1, averageIntervalData])
        db.session.commit()
        # make query for non-existent cooler
        response = self.client.get(
            "/api/averageIntervalData/?cooler_id=500&intervals_id=1",
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
            higlass_uuid="asdf1234",
            filetype="cooler",
            user_id=1,
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            higlass_uuid="testHiglass1",
            windowsize=200000,
        )
        averageIntervalData = AverageIntervalData(
            name="testAverageIntervalData1",
            binsize=10000,
            file_path="testPath1",
            cooler_id=1,
            intervals_id=1,
            value_type="ICCF",
        )
        db.session.add_all([dataset1, intervals1, averageIntervalData])
        db.session.commit()
        # make query for non-existent cooler
        response = self.client.get(
            "/api/averageIntervalData/?cooler_id=1&intervals_id=500",
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
            higlass_uuid="asdf1234",
            filetype="cooler",
            user_id=1,
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            higlass_uuid="testHiglass1",
            windowsize=200000,
        )
        averageIntervalData = AverageIntervalData(
            name="testAverageIntervalData1",
            binsize=10000,
            file_path="testPath1",
            cooler_id=1,
            intervals_id=1,
            value_type="ICCF",
        )
        db.session.add_all([dataset1, intervals1, averageIntervalData])
        db.session.commit()
        # make query for non-existent cooler
        response = self.client.get(
            "/api/averageIntervalData/", headers=token_headers, content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_no_cooler_provided(self):
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        dataset1 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            higlass_uuid="asdf1234",
            filetype="cooler",
            user_id=1,
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            higlass_uuid="testHiglass1",
            windowsize=200000,
        )
        averageIntervalData = AverageIntervalData(
            name="testAverageIntervalData1",
            binsize=10000,
            file_path="testPath1",
            cooler_id=1,
            intervals_id=1,
            value_type="ICCF",
        )
        db.session.add_all([dataset1, intervals1, averageIntervalData])
        db.session.commit()
        # make query for non-existent cooler
        response = self.client.get(
            "/api/averageIntervalData/?intervals_id=1",
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
            higlass_uuid="asdf1234",
            filetype="cooler",
            user_id=1,
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            higlass_uuid="testHiglass1",
            windowsize=200000,
        )
        averageIntervalData = AverageIntervalData(
            name="testAverageIntervalData1",
            binsize=10000,
            file_path="testPath1",
            cooler_id=1,
            intervals_id=1,
            value_type="ICCF",
        )
        db.session.add_all([dataset1, intervals1, averageIntervalData])
        db.session.commit()
        # make query for non-existent cooler
        response = self.client.get(
            "/api/averageIntervalData/?cooler_id=1",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_forbidden_cooler_not_owned(self):
        """Tests whether 403 response is sent if
        cooler file is not owned by user in token."""
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
            higlass_uuid="asdf1234",
            filetype="cooler",
            user_id=1,
        )
        dataset2 = Dataset(
            dataset_name="test2",
            file_path="/test/path/2",
            higlass_uuid="asdf12345",
            filetype="cooler",
            user_id=2,
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            higlass_uuid="testHiglass1",
            windowsize=200000,
        )
        averageIntervalData = AverageIntervalData(
            name="testAverageIntervalData1",
            binsize=10000,
            file_path="testPath1",
            cooler_id=1,
            intervals_id=1,
            value_type="ICCF",
        )
        db.session.add_all([dataset1, dataset2, intervals1, averageIntervalData])
        db.session.commit()
        # make query for non-existent cooler
        response = self.client.get(
            "/api/averageIntervalData/?cooler_id=2&intervals_id=1",
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
            higlass_uuid="asdf1234",
            filetype="cooler",
            user_id=1,
        )
        dataset2 = Dataset(
            dataset_name="test2",
            file_path="/test/path/2",
            higlass_uuid="asdf12345",
            filetype="cooler",
            user_id=2,
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            higlass_uuid="testHiglass1",
            windowsize=200000,
        )
        intervals2 = Intervals(
            name="testRegion2",
            dataset_id=2,
            file_path="test_path_2.bedd2db",
            higlass_uuid="testHiglass2",
            windowsize=200000,
        )
        averageIntervalData = AverageIntervalData(
            name="testAverageIntervalData1",
            binsize=10000,
            file_path="testPath1",
            cooler_id=1,
            intervals_id=1,
            value_type="ICCF",
        )
        db.session.add_all([dataset1, dataset2, intervals1, intervals2, averageIntervalData])
        db.session.commit()
        # make query for non-existent cooler
        response = self.client.get(
            "/api/averageIntervalData/?cooler_id=1&intervals_id=2", headers=token_headers, content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_get_averageIntervalData_allowed_for_public_unowned(self):
        """Tests whether listing averageIntervalData is allowed for an unowned but public dataset."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        dataset1 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            higlass_uuid="asdf1234",
            filetype="cooler",
            public=True,
            user_id=2,
        )
        dataset2 = Dataset(
            dataset_name="test2",
            file_path="/test/path/2",
            higlass_uuid="asdf12345",
            filetype="cooler",
            public=True,
            user_id=2,
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            higlass_uuid="testHiglass1",
            windowsize=200000,
        )
        intervals2 = Intervals(
            name="testRegion2",
            dataset_id=2,
            file_path="test_path_2.bedd2db",
            higlass_uuid="testHiglass2",
            windowsize=200000,
        )
        averageIntervalData1 = AverageIntervalData(
            name="testAverageIntervalData1",
            binsize=10000,
            file_path="testPath1",
            cooler_id=1,
            intervals_id=1,
            value_type="ICCF",
        )
        averageIntervalData2 = AverageIntervalData(
            name="testAverageIntervalData2",
            binsize=10000,
            file_path="testPath2",
            cooler_id=1,
            intervals_id=2,
            value_type="ICCF",
        )
        averageIntervalData3 = AverageIntervalData(
            name="testAverageIntervalData3",
            binsize=10000,
            file_path="testPath3",
            cooler_id=2,
            intervals_id=1,
            value_type="ICCF",
        )
        averageIntervalData4 = AverageIntervalData(
            name="testAverageIntervalData4",
            binsize=10000,
            file_path="testPath4",
            cooler_id=2,
            intervals_id=2,
            value_type="ICCF",
        )
        db.session.add_all(
            [
                dataset1,
                dataset2,
                intervals1,
                intervals2,
                averageIntervalData1,
                averageIntervalData2,
                averageIntervalData3,
                averageIntervalData4,
            ]
        )
        db.session.commit()
        # make query 1
        response = self.client.get(
            "/api/averageIntervalData/?cooler_id=1&intervals_id=1", headers=token_headers, content_type="application/json",
        )
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]["id"], 1)
        # make query 2
        response = self.client.get(
            "/api/averageIntervalData/?cooler_id=1&intervals_id=2", headers=token_headers, content_type="application/json",
        )
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]["id"], 2)


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
            higlass_uuid="asdf1234",
            filetype="cooler",
            user_id=5,
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            higlass_uuid="testHiglass1",
            windowsize=200000,
        )
        averageIntervalData = AverageIntervalData(
            name="testAverageIntervalData1",
            binsize=10000,
            file_path="testPath1",
            cooler_id=1,
            intervals_id=1,
            value_type="ICCF",
        )
        db.session.add_all([dataset1, intervals1, averageIntervalData])
        db.session.commit()
        # make request
        response = self.client.get(
            "/api/averageIntervalData/1/", headers=token_headers, content_type="application/json",
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
            higlass_uuid="asdf1234",
            filetype="cooler",
            user_id=1,
        )
        dataset2 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            higlass_uuid="asdf12345",
            filetype="bedfile",
            user_id=5,
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=2,
            file_path="test_path_1.bedd2db",
            higlass_uuid="testHiglass1",
            windowsize=200000,
        )
        averageIntervalData = AverageIntervalData(
            name="testAverageIntervalData1",
            binsize=10000,
            file_path="testPath1",
            cooler_id=1,
            intervals_id=1,
            value_type="ICCF",
        )
        db.session.add_all([dataset1, dataset2, intervals1, averageIntervalData])
        db.session.commit()
        # make request
        response = self.client.get(
            "/api/averageIntervalData/1/", headers=token_headers, content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_correct_data_returned(self):
        """Correct data is returned from an owned averageIntervalData"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # create datafile
        test_data = pd.DataFrame(
            {
                "variable": [0, 0, 0, 0],
                "group": [0, 1, 2, 3],
                "value": [1.66, 2.2, 3.8, 4.5],
            }
        )
        data_path = os.path.join(TempDirTestCase.TEMP_PATH, "test.csv")
        test_data.to_csv(data_path, index=False)
        # add data
        dataset1 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            higlass_uuid="asdf1234",
            filetype="cooler",
            user_id=1,
        )
        dataset2 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            higlass_uuid="asdf12345",
            filetype="bedfile",
            user_id=1,
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=2,
            file_path="test_path_1.bedd2db",
            higlass_uuid="testHiglass1",
            windowsize=200000,
        )
        averageIntervalData = AverageIntervalData(
            name="testAverageIntervalData1",
            binsize=10000,
            file_path=data_path,
            cooler_id=1,
            intervals_id=1,
            value_type="ICCF",
        )
        db.session.add_all([dataset1, dataset2, intervals1, averageIntervalData])
        db.session.commit()
        # make request
        response = self.client.get(
            "/api/averageIntervalData/1/", headers=token_headers, content_type="application/json",
        )
        expected = test_data.to_json()
        self.assertEqual(response.json, expected)

    def test_public_unowned_data_returned(self):
        """Test whether public, unowned data is returned correctly."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # create datafile
        test_data = pd.DataFrame(
            {
                "variable": [0, 0, 0, 0],
                "group": [0, 1, 2, 3],
                "value": [1.66, 2.2, 3.8, 4.5],
            }
        )
        data_path = os.path.join(TempDirTestCase.TEMP_PATH, "test.csv")
        test_data.to_csv(data_path, index=False)
        # add data
        dataset1 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            higlass_uuid="asdf1234",
            filetype="cooler",
            public=True,
            user_id=2,
        )
        dataset2 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            higlass_uuid="asdf12345",
            filetype="bedfile",
            public=True,
            user_id=2,
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=2,
            file_path="test_path_1.bedd2db",
            higlass_uuid="testHiglass1",
            windowsize=200000,
        )
        averageIntervalData = AverageIntervalData(
            name="testAverageIntervalData1",
            binsize=10000,
            file_path=data_path,
            cooler_id=1,
            intervals_id=1,
            value_type="ICCF",
        )
        db.session.add_all([dataset1, dataset2, intervals1, averageIntervalData])
        db.session.commit()
        # make request
        response = self.client.get(
            "/api/averageIntervalData/1/", headers=token_headers, content_type="application/json",
        )
        expected = test_data.to_json()
        self.assertEqual(response.json, expected)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
