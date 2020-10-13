import pdb
import unittest
from test_helpers import LoginTestCase

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
        response = self.client.get("/api/pileups/1/2/", content_type="application/json")
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
        )
        db.session.add_all([dataset1, pileupregion1, pileup])
        db.session.commit()
        # make query for non-existent cooler
        response = self.client.get(
            "/api/pileups/500/1/",
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
        )
        db.session.add_all([dataset1, pileupregion1, pileup])
        db.session.commit()
        # make query for non-existent cooler
        response = self.client.get(
            "/api/pileups/1/500/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

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
        )
        db.session.add_all([dataset1, dataset2, pileupregion1, pileup])
        db.session.commit()
        # make query for non-existent cooler
        response = self.client.get(
            "/api/pileups/2/1/", headers=token_headers, content_type="application/json",
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
        )
        db.session.add_all([dataset1, dataset2, pileupregion1, pileupregion2, pileup])
        db.session.commit()
        # make query for non-existent cooler
        response = self.client.get(
            "/api/pileups/1/2/", headers=token_headers, content_type="application/json",
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
        )
        pileup2 = Pileup(
            name="testPileup2",
            binsize=10000,
            file_path="testPath2",
            cooler_id=1,
            pileupregion_id=2,
        )
        pileup3 = Pileup(
            name="testPileup3",
            binsize=10000,
            file_path="testPath3",
            cooler_id=2,
            pileupregion_id=1,
        )
        pileup4 = Pileup(
            name="testPileup4",
            binsize=10000,
            file_path="testPath4",
            cooler_id=2,
            pileupregion_id=2,
        )
        db.session.add_all([dataset1, dataset2, pileupregion1, pileupregion2, pileup1, pileup2, pileup3, pileup4])
        db.session.commit()
        # make query 1
        response = self.client.get(
            "/api/pileups/1/1/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]["id"], 1)
        # make query 2
        response = self.client.get(
            "/api/pileups/1/2/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]["id"], 2)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
