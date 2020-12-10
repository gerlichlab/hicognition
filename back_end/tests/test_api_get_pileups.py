import os
import pdb
import unittest
import pandas as pd
from test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
import sys

sys.path.append("./")
from app import db
from app.models import Dataset, Pileupregion, Pileup


class TestGetPileups(LoginTestCase):
    """Tests for /api/pileups route to list
    pileups."""

    def test_no_auth(self):
        """No authentication provided, response should be 401"""
        # protected route
        response = self.client.get(
            "/api/pileups/?cooler_id=1&pileupregion_id=2",
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
        pileupregion1 = Pileupregion(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            higlass_uuid="testHiglass1",
            windowsize=200000,
        )
        pileup = Pileup(
            name="testPileup1",
            binsize=10000,
            file_path="testPath1",
            cooler_id=1,
            pileupregion_id=1,
            value_type="ICCF",
        )
        db.session.add_all([dataset1, pileupregion1, pileup])
        db.session.commit()
        # make query for non-existent cooler
        response = self.client.get(
            "/api/pileups/?cooler_id=500&pileupregion_id=1",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_pileupregion_does_not_exist(self):
        """Test whether 404 if pileupregion dataset does not exist"""
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
        pileupregion1 = Pileupregion(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            higlass_uuid="testHiglass1",
            windowsize=200000,
        )
        pileup = Pileup(
            name="testPileup1",
            binsize=10000,
            file_path="testPath1",
            cooler_id=1,
            pileupregion_id=1,
            value_type="ICCF",
        )
        db.session.add_all([dataset1, pileupregion1, pileup])
        db.session.commit()
        # make query for non-existent cooler
        response = self.client.get(
            "/api/pileups/?cooler_id=1&pileupregion_id=500",
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
        pileupregion1 = Pileupregion(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            higlass_uuid="testHiglass1",
            windowsize=200000,
        )
        pileup = Pileup(
            name="testPileup1",
            binsize=10000,
            file_path="testPath1",
            cooler_id=1,
            pileupregion_id=1,
            value_type="ICCF",
        )
        db.session.add_all([dataset1, pileupregion1, pileup])
        db.session.commit()
        # make query for non-existent cooler
        response = self.client.get(
            "/api/pileups/", headers=token_headers, content_type="application/json",
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
        pileupregion1 = Pileupregion(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            higlass_uuid="testHiglass1",
            windowsize=200000,
        )
        pileup = Pileup(
            name="testPileup1",
            binsize=10000,
            file_path="testPath1",
            cooler_id=1,
            pileupregion_id=1,
            value_type="ICCF",
        )
        db.session.add_all([dataset1, pileupregion1, pileup])
        db.session.commit()
        # make query for non-existent cooler
        response = self.client.get(
            "/api/pileups/?pileupregion_id=1",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_no_pileupregion_provided(self):
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
        pileupregion1 = Pileupregion(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            higlass_uuid="testHiglass1",
            windowsize=200000,
        )
        pileup = Pileup(
            name="testPileup1",
            binsize=10000,
            file_path="testPath1",
            cooler_id=1,
            pileupregion_id=1,
            value_type="ICCF",
        )
        db.session.add_all([dataset1, pileupregion1, pileup])
        db.session.commit()
        # make query for non-existent cooler
        response = self.client.get(
            "/api/pileups/?cooler_id=1",
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
        pileupregion1 = Pileupregion(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            higlass_uuid="testHiglass1",
            windowsize=200000,
        )
        pileup = Pileup(
            name="testPileup1",
            binsize=10000,
            file_path="testPath1",
            cooler_id=1,
            pileupregion_id=1,
            value_type="ICCF",
        )
        db.session.add_all([dataset1, dataset2, pileupregion1, pileup])
        db.session.commit()
        # make query for non-existent cooler
        response = self.client.get(
            "/api/pileups/?cooler_id=2&pileupregion_id=1",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_forbidden_pileupregion_not_owned(self):
        """Test whether 403 is sent if pileupregions are not owned."""
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
        pileupregion1 = Pileupregion(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            higlass_uuid="testHiglass1",
            windowsize=200000,
        )
        pileupregion2 = Pileupregion(
            name="testRegion2",
            dataset_id=2,
            file_path="test_path_2.bedd2db",
            higlass_uuid="testHiglass2",
            windowsize=200000,
        )
        pileup = Pileup(
            name="testPileup1",
            binsize=10000,
            file_path="testPath1",
            cooler_id=1,
            pileupregion_id=1,
            value_type="ICCF",
        )
        db.session.add_all([dataset1, dataset2, pileupregion1, pileupregion2, pileup])
        db.session.commit()
        # make query for non-existent cooler
        response = self.client.get(
            "/api/pileups/?cooler_id=1&pileupregion_id=2", headers=token_headers, content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_get_pileups_allowed(self):
        """Correct call for pileups results in correct pileups returned."""
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
            dataset_name="test2",
            file_path="/test/path/2",
            higlass_uuid="asdf12345",
            filetype="cooler",
            user_id=1,
        )
        pileupregion1 = Pileupregion(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            higlass_uuid="testHiglass1",
            windowsize=200000,
        )
        pileupregion2 = Pileupregion(
            name="testRegion2",
            dataset_id=2,
            file_path="test_path_2.bedd2db",
            higlass_uuid="testHiglass2",
            windowsize=200000,
        )
        pileup1 = Pileup(
            name="testPileup1",
            binsize=10000,
            file_path="testPath1",
            cooler_id=1,
            pileupregion_id=1,
            value_type="ICCF",
        )
        pileup2 = Pileup(
            name="testPileup2",
            binsize=10000,
            file_path="testPath2",
            cooler_id=1,
            pileupregion_id=2,
            value_type="ICCF",
        )
        pileup3 = Pileup(
            name="testPileup3",
            binsize=10000,
            file_path="testPath3",
            cooler_id=2,
            pileupregion_id=1,
            value_type="ICCF",
        )
        pileup4 = Pileup(
            name="testPileup4",
            binsize=10000,
            file_path="testPath4",
            cooler_id=2,
            pileupregion_id=2,
            value_type="ICCF",
        )
        db.session.add_all(
            [
                dataset1,
                dataset2,
                pileupregion1,
                pileupregion2,
                pileup1,
                pileup2,
                pileup3,
                pileup4,
            ]
        )
        db.session.commit()
        # make query 1
        response = self.client.get(
            "/api/pileups/?cooler_id=1&pileupregion_id=1", headers=token_headers, content_type="application/json",
        )
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]["id"], 1)
        # make query 2
        response = self.client.get(
            "/api/pileups/?cooler_id=1&pileupregion_id=2", headers=token_headers, content_type="application/json",
        )
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]["id"], 2)


class TestGetPileupData(LoginTestCase, TempDirTestCase):
    """Test to check whether retrieving of pileup data
    works."""

    def test_no_auth(self):
        """No authentication provided, response should be 401"""
        # protected route
        response = self.client.get(
            "/api/pileups/1/", content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

    def test_pileup_does_not_exist(self):
        """Test 404 is returned if pileup does not exist."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # make request
        response = self.client.get(
            "/api/pileups/500/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_cooler_not_owned(self):
        """Cooler dataset underlying pileup is not owned"""
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
        pileupregion1 = Pileupregion(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            higlass_uuid="testHiglass1",
            windowsize=200000,
        )
        pileup = Pileup(
            name="testPileup1",
            binsize=10000,
            file_path="testPath1",
            cooler_id=1,
            pileupregion_id=1,
            value_type="ICCF",
        )
        db.session.add_all([dataset1, pileupregion1, pileup])
        db.session.commit()
        # make request
        response = self.client.get(
            "/api/pileups/1/", headers=token_headers, content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_pileupregion_not_owned(self):
        """Pileupregion dataset underlying pileup is not owned"""
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
        pileupregion1 = Pileupregion(
            name="testRegion1",
            dataset_id=2,
            file_path="test_path_1.bedd2db",
            higlass_uuid="testHiglass1",
            windowsize=200000,
        )
        pileup = Pileup(
            name="testPileup1",
            binsize=10000,
            file_path="testPath1",
            cooler_id=1,
            pileupregion_id=1,
            value_type="ICCF",
        )
        db.session.add_all([dataset1, dataset2, pileupregion1, pileup])
        db.session.commit()
        # make request
        response = self.client.get(
            "/api/pileups/1/", headers=token_headers, content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_correct_data_returned(self):
        """Correct data is returned from an owned pileup"""
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
        pileupregion1 = Pileupregion(
            name="testRegion1",
            dataset_id=2,
            file_path="test_path_1.bedd2db",
            higlass_uuid="testHiglass1",
            windowsize=200000,
        )
        pileup = Pileup(
            name="testPileup1",
            binsize=10000,
            file_path=data_path,
            cooler_id=1,
            pileupregion_id=1,
            value_type="ICCF",
        )
        db.session.add_all([dataset1, dataset2, pileupregion1, pileup])
        db.session.commit()
        # make request
        response = self.client.get(
            "/api/pileups/1/", headers=token_headers, content_type="application/json",
        )
        expected = test_data.to_json()
        self.assertEqual(response.json, expected)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
