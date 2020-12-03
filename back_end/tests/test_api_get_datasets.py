from test_helpers import LoginTestCase
# add path to import app
import sys
sys.path.append("./")
from app import db
from app.models import Dataset, Task


class TestGetDatasets(LoginTestCase):
    """Tests for /api/datasets route to list
    datasets."""

    def add_test_datasets(self):
        """adds test datasets to db"""
        dataset1 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            higlass_uuid="asdf1234",
            filetype="cooler",
            processing_state="finished",
            user_id=1
        )
        dataset2 = Dataset(
            dataset_name="test2",
            file_path="/test/path/2",
            higlass_uuid="fdsa4321",
            filetype="cooler",
            processing_state="finished",
            user_id=1
        )
        dataset3 = Dataset(
            dataset_name="test3",
            file_path="/test/path/3",
            higlass_uuid="fdsa8765",
            filetype="bedfile",
            processing_state="finished",
            user_id=1
        )
        db.session.add(dataset1)
        db.session.add(dataset2)
        db.session.add(dataset3)
        db.session.commit()

    def test_no_auth(self):
        """No authentication provided, response should be 401"""
        # protected route
        response = self.client.get("/api/datasets/", content_type="application/json")
        self.assertEqual(response.status_code, 401)

    def test_get_coolers(self):
        """Authenticated user gets cooler datasets."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add new datasets
        self.add_test_datasets()
        # get datasets
        response = self.client.get(
            "/api/datasets/cooler",
            headers=token_headers,
            content_type="application/json",
        )
        # check response
        self.assertEqual(response.status_code, 200)
        expected = [
            {
                "dataset_name": "test1",
                "file_path": "/test/path/1",
                "filetype": "cooler",
                "higlass_uuid": "asdf1234",
                "id": 1,
                "user_id": 1,
                "processing_state": "finished"
            },
            {
                "dataset_name": "test2",
                "file_path": "/test/path/2",
                "filetype": "cooler",
                "higlass_uuid": "fdsa4321",
                "id": 2,
                "user_id": 1,
                "processing_state": "finished"
            },
        ]
        self.assertEqual(response.json, expected)

    def test_get_bedfiles(self):
        """Authenticated user gets bed datasets."""
        # add new user
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add new datasets
        self.add_test_datasets()
        # get datasets
        response = self.client.get(
            "/api/datasets/bed", headers=token_headers, content_type="application/json",
        )
        # check response
        self.assertEqual(response.status_code, 200)
        expected = [
            {
                "dataset_name": "test3",
                "file_path": "/test/path/3",
                "filetype": "bedfile",
                "higlass_uuid": "fdsa8765",
                "id": 3,
                "user_id": 1,
                "processing_state": "finished"
            },
        ]
        self.assertEqual(response.json, expected)

    def test_get_all_datasets(self):
        """Authenticated user gets cooler and bed datasets"""
        # add new user
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add new datasets
        self.add_test_datasets()
        # get datasets
        response = self.client.get(
            "/api/datasets/", headers=token_headers, content_type="application/json",
        )
        # check response
        self.assertEqual(response.status_code, 200)
        expected = [
            {
                "dataset_name": "test1",
                "file_path": "/test/path/1",
                "filetype": "cooler",
                "higlass_uuid": "asdf1234",
                "id": 1,
                "user_id": 1,
                "processing_state": "finished"
            },
            {
                "dataset_name": "test2",
                "file_path": "/test/path/2",
                "filetype": "cooler",
                "higlass_uuid": "fdsa4321",
                "id": 2,
                "user_id": 1,
                "processing_state": "finished"
            },
            {
                "dataset_name": "test3",
                "file_path": "/test/path/3",
                "filetype": "bedfile",
                "higlass_uuid": "fdsa8765",
                "id": 3,
                "user_id": 1,
                "processing_state": "finished"
            },
        ]
        self.assertEqual(response.json, expected)

    def test_wrong_path(self):
        """Authenticated user tries to get datasets with wrong
        parameters."""
        # add new user
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add new datasets
        self.add_test_datasets()
        # get datasets
        response = self.client.get(
            "/api/datasets/asdf",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_user_can_get_only_own_datasets(self):
        """Authenticated user can only get own datasets"""
        token1 = self.add_and_authenticate("test", "asdf")
        token2 = self.add_and_authenticate("test2", "fdsa")
        # add datasets
        dataset1 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            higlass_uuid="asdf1234",
            filetype="cooler",
            processing_state="finished",
            user_id=1
        )
        dataset2 = Dataset(
            dataset_name="test2",
            file_path="/test/path/2",
            higlass_uuid="fdsa4321",
            filetype="cooler",
            processing_state="finished",
            user_id=2
        )
        dataset3 = Dataset(
            dataset_name="test3",
            file_path="/test/path/3",
            higlass_uuid="fdsa8765",
            filetype="bedfile",
            processing_state="finished",
            user_id=1
        )
        dataset4 = Dataset(
            dataset_name="test4",
            file_path="/test/path/4",
            higlass_uuid="fdsa8768",
            filetype="bedfile",
            processing_state="finished",
            user_id=2
        )
        db.session.add(dataset1)
        db.session.add(dataset2)
        db.session.add(dataset3)
        db.session.add(dataset4)
        db.session.commit()
        # get datasets with user_token 1
        token_headers = self.get_token_header(token1)
        # get datasets
        response = self.client.get(
            "/api/datasets/", headers=token_headers, content_type="application/json",
        )
        # check response
        self.assertEqual(response.status_code, 200)
        expected = [
            {
                "dataset_name": "test1",
                "file_path": "/test/path/1",
                "filetype": "cooler",
                "higlass_uuid": "asdf1234",
                "id": 1,
                "user_id": 1,
                "processing_state": "finished"
            },
            {
                "dataset_name": "test3",
                "file_path": "/test/path/3",
                "filetype": "bedfile",
                "higlass_uuid": "fdsa8765",
                "id": 3,
                "user_id": 1,
                "processing_state": "finished"
            },
        ]
        self.assertEqual(response.json, expected)
        # check response for coolers
        response = self.client.get(
            "/api/datasets/cooler", headers=token_headers, content_type="application/json",
        )
        # check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [expected[0]])
        # check response for bedfiles
        response = self.client.get(
            "/api/datasets/bed", headers=token_headers, content_type="application/json",
        )
        # check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [expected[1]])
