import pdb
import unittest
from test_helpers import LoginTestCase
# add path to import app
import sys
sys.path.append("./")
from app import db
from app.models import User, Dataset, Task, Pileupregion


class TestGetPileupregions(LoginTestCase):
    """Tests for /api/datasets route to list
    datasets."""

    def test_no_auth(self):
        """No authentication provided, response should be 401"""
        # protected route
        response = self.client.get("/api/datasets/", content_type="application/json")
        self.assertEqual(response.status_code, 401)

    def test_correct_pileupregions_single_dataset(self):
        """Correct pileupregions are returned for single dataset."""
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
            user_id=1
        )
        pileupregion1 = Pileupregion(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            higlass_uuid="testHiglass1",
            windowsize=200000
        )
        pileupregion2 = Pileupregion(
            name="testRegion2",
            dataset_id=1,
            file_path="test_path_2.bedd2db",
            higlass_uuid="testHiglass2",
            windowsize=400000
        )
        db.session.add_all([dataset1, pileupregion1, pileupregion2])
        db.session.commit()
        # get pileupregions 
        response = self.client.get(
            "/api/pileupregions",
            headers=token_headers,
            content_type="application/json",
        )
        # check whether they are correct
        expected = [
            {
                "id": 1,
                "source_dataset": 1,
                "dataset_name": "testRegion1",
                "file_path": "test_path_1.bedd2db",
                "higlass_uuid": "testHiglass1",
                "windowsize": 200000
            },
            {
                "id": 2,
                "source_dataset": 1,
                "dataset_name": "testRegion2",
                "file_path": "test_path_2.bedd2db",
                "higlass_uuid": "testHiglass2",
                "windowsize": 400000
            }
        ]
        self.assertEqual(response.json, expected)

    def test_correct_pileupregions_two_datasets(self):
        """Tests whether correct pileupregions are returned if
        there are multiple datasets from different users."""
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
            user_id=1
        )
        dataset2 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            higlass_uuid="asdf1235",
            filetype="cooler",
            user_id=2
        )
        pileupregion1 = Pileupregion(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            higlass_uuid="testHiglass1",
            windowsize=200000
        )
        pileupregion2 = Pileupregion(
            name="testRegion2",
            dataset_id=1,
            file_path="test_path_2.bedd2db",
            higlass_uuid="testHiglass2",
            windowsize=400000
        )
        pileupregion3 = Pileupregion(
            name="testRegion3",
            dataset_id=2,
            file_path="test_path_3.bedd2db",
            higlass_uuid="testHiglass3",
            windowsize=400000
        )
        db.session.add_all([dataset1, dataset2, pileupregion1, pileupregion2, pileupregion3])
        db.session.commit()
        # get pileupregions
        response = self.client.get(
            "/api/pileupregions",
            headers=token_headers,
            content_type="application/json",
        )
        # check whether they are correct
        expected = [
            {
                "id": 1,
                "source_dataset": 1,
                "dataset_name": "testRegion1",
                "file_path": "test_path_1.bedd2db",
                "higlass_uuid": "testHiglass1",
                "windowsize": 200000
            },
            {
                "id": 2,
                "source_dataset": 1,
                "dataset_name": "testRegion2",
                "file_path": "test_path_2.bedd2db",
                "higlass_uuid": "testHiglass2",
                "windowsize": 400000
            }
        ]
        self.assertEqual(response.json, expected)
        # test other user
        response = self.client.get(
            "/api/pileupregions",
            headers=token_headers2,
            content_type="application/json",
        )
        # check whether they are correct
        expected = [
            {
                "id": 3,
                "source_dataset": 2,
                "dataset_name": "testRegion3",
                "file_path": "test_path_3.bedd2db",
                "higlass_uuid": "testHiglass3",
                "windowsize": 400000
            }
        ]
        self.assertEqual(response.json, expected)

class TestGetSpecificPileupregions(LoginTestCase):
    """Tests getting pileupregions of a specific dataset."""

    def test_no_auth(self):
        """No authentication provided, response should be 401"""
        # protected route
        response = self.client.get("/api/datasets/1/pileupregions", content_type="application/json")
        self.assertEqual(response.status_code, 401)

    def test_404_if_wrong_id(self):
        """Tests whether status_code 404 is returned
        if id is wrong."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # get pileupregions
        response = self.client.get(
            "/api/datasets/500/pileupregions",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_403_if_not_owned_dataset(self):
        """Tests whether status_code 403 is returned
        if dataset is not owned."""
         # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token2 = self.add_and_authenticate("test2", "fdsa")
        # create token header
        token_headers2 = self.get_token_header(token2)
        # add data
        dataset1 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            higlass_uuid="asdf1234",
            filetype="cooler",
            user_id=1
        )
        pileupregion1 = Pileupregion(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            higlass_uuid="testHiglass1",
            windowsize=200000
        )
        db.session.add_all([dataset1, pileupregion1])
        db.session.commit()
        # get pileupregions
        response = self.client.get(
            "/api/datasets/1/pileupregions",
            headers=token_headers2,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_correct_pileupregions_returned(self):
        """Test whether only pileupregions belonging
        to a particular dataset are returned."""
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
            user_id=1
        )
        dataset2 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            higlass_uuid="asdf1235",
            filetype="cooler",
            user_id=1
        )
        pileupregion1 = Pileupregion(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            higlass_uuid="testHiglass1",
            windowsize=200000
        )
        pileupregion2 = Pileupregion(
            name="testRegion2",
            dataset_id=1,
            file_path="test_path_2.bedd2db",
            higlass_uuid="testHiglass2",
            windowsize=400000
        )
        pileupregion3 = Pileupregion(
            name="testRegion3",
            dataset_id=2,
            file_path="test_path_3.bedd2db",
            higlass_uuid="testHiglass3",
            windowsize=400000
        )
        db.session.add_all([dataset1, dataset2, pileupregion1, pileupregion2, pileupregion3])
        db.session.commit()
        # get pileupregions
        response = self.client.get(
            "/api/datasets/1/pileupregions",
            headers=token_headers,
            content_type="application/json",
        )
        # compare response
        expected = [
            {
                "id": 1,
                "source_dataset": 1,
                "dataset_name": "testRegion1",
                "file_path": "test_path_1.bedd2db",
                "higlass_uuid": "testHiglass1",
                "windowsize": 200000
            },
            {
                "id": 2,
                "source_dataset": 1,
                "dataset_name": "testRegion2",
                "file_path": "test_path_2.bedd2db",
                "higlass_uuid": "testHiglass2",
                "windowsize": 400000
            }
        ]
        self.assertEqual(response.json, expected)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
