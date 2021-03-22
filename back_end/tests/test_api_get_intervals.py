import unittest
from test_helpers import LoginTestCase
# add path to import app
import sys
sys.path.append("./")
from app import db
from app.models import Dataset, Intervals


class TestGetIntervals(LoginTestCase):
    """Tests for /api/intervals route to list
    intervals."""

    def test_no_auth(self):
        """No authentication provided, response should be 401"""
        # protected route
        response = self.client.get("/api/intervals/", content_type="application/json")
        self.assertEqual(response.status_code, 401)

    def test_correct_intervals_single_dataset(self):
        """Correct intervals are returned for single dataset."""
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
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            higlass_uuid="testHiglass1",
            windowsize=200000
        )
        intervals2 = Intervals(
            name="testRegion2",
            dataset_id=1,
            file_path="test_path_2.bedd2db",
            higlass_uuid="testHiglass2",
            windowsize=400000
        )
        db.session.add_all([dataset1, intervals1, intervals2])
        db.session.commit()
        # get intervals 
        response = self.client.get(
            "/api/intervals/",
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

    def test_correct_intervals_two_datasets(self):
        """Tests whether correct intervals are returned if
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
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            higlass_uuid="testHiglass1",
            windowsize=200000
        )
        intervals2 = Intervals(
            name="testRegion2",
            dataset_id=1,
            file_path="test_path_2.bedd2db",
            higlass_uuid="testHiglass2",
            windowsize=400000
        )
        intervals3 = Intervals(
            name="testRegion3",
            dataset_id=2,
            file_path="test_path_3.bedd2db",
            higlass_uuid="testHiglass3",
            windowsize=400000
        )
        db.session.add_all([dataset1, dataset2, intervals1, intervals2, intervals3])
        db.session.commit()
        # get intervals
        response = self.client.get(
            "/api/intervals/",
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
            "/api/intervals/",
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

    def test_get_public_intervals(self):
        """Tests whether intervals are returned for a public but not
        owned dataset."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token2 = self.add_and_authenticate("test2", "fdsa")
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
            public=True,
            user_id=2
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            higlass_uuid="testHiglass1",
            windowsize=200000
        )
        intervals2 = Intervals(
            name="testRegion2",
            dataset_id=1,
            file_path="test_path_2.bedd2db",
            higlass_uuid="testHiglass2",
            windowsize=400000
        )
        intervals3 = Intervals(
            name="testRegion3",
            dataset_id=2,
            file_path="test_path_3.bedd2db",
            higlass_uuid="testHiglass3",
            windowsize=400000
        )
        db.session.add_all([dataset1, dataset2, intervals1, intervals2, intervals3])
        db.session.commit()
        # get intervals
        response = self.client.get(
            "/api/intervals/",
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
            },
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


class TestGetSpecificIntervals(LoginTestCase):
    """Tests getting intervals of a specific dataset."""

    def test_no_auth(self):
        """No authentication provided, response should be 401"""
        # protected route
        response = self.client.get("/api/datasets/1/intervals/", content_type="application/json")
        self.assertEqual(response.status_code, 401)

    def test_404_if_wrong_id(self):
        """Tests whether status_code 404 is returned
        if id is wrong."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # get intervals
        response = self.client.get(
            "/api/datasets/500/intervals/",
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
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            higlass_uuid="testHiglass1",
            windowsize=200000
        )
        db.session.add_all([dataset1, intervals1])
        db.session.commit()
        # get intervals
        response = self.client.get(
            "/api/datasets/1/intervals/",
            headers=token_headers2,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_correct_intervals_returned(self):
        """Test whether only intervals belonging
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
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            higlass_uuid="testHiglass1",
            windowsize=200000
        )
        intervals2 = Intervals(
            name="testRegion2",
            dataset_id=1,
            file_path="test_path_2.bedd2db",
            higlass_uuid="testHiglass2",
            windowsize=400000
        )
        intervals3 = Intervals(
            name="testRegion3",
            dataset_id=2,
            file_path="test_path_3.bedd2db",
            higlass_uuid="testHiglass3",
            windowsize=400000
        )
        db.session.add_all([dataset1, dataset2, intervals1, intervals2, intervals3])
        db.session.commit()
        # get intervals
        response = self.client.get(
            "/api/datasets/1/intervals/",
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

    def test_access_to_public_but_unowned_intervals(self):
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
            dataset_name="test2",
            file_path="/test/path/2",
            higlass_uuid="asdf1235",
            filetype="cooler",
            public=True,
            user_id=2
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            higlass_uuid="testHiglass1",
            windowsize=200000
        )
        intervals2 = Intervals(
            name="testRegion2",
            dataset_id=1,
            file_path="test_path_2.bedd2db",
            higlass_uuid="testHiglass2",
            windowsize=400000
        )
        intervals3 = Intervals(
            name="testRegion3",
            dataset_id=2,
            file_path="test_path_3.bedd2db",
            higlass_uuid="testHiglass3",
            windowsize=400000
        )
        db.session.add_all([dataset1, dataset2, intervals1, intervals2, intervals3])
        db.session.commit()
        # get intervals
        response = self.client.get(
            "/api/datasets/2/intervals/",
            headers=token_headers,
            content_type="application/json",
        )
        # compare response
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


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
