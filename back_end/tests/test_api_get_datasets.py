import unittest
from unittest.mock import patch
from test_helpers import LoginTestCase

# add path to import app
import sys

sys.path.append("./")
from app import db
from app.models import Dataset, Task, Session


class TestGetDatasets(LoginTestCase):
    """Tests for /api/datasets route to list
    datasets."""

    def setUp(self):
        """adds test datasets to db"""
        super().setUp()
        # add owned coolers
        self.owned_cooler_1 = Dataset(
            id=1,
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="cooler",
            processing_state="finished",
            user_id=1,
        )
        self.owned_cooler_2 = Dataset(
            id=2,
            dataset_name="test2",
            file_path="/test/path/2",
            filetype="cooler",
            processing_state="finished",
            user_id=1,
        )
        # add unowned coolers
        self.unowned_cooler = Dataset(
            id=3,
            dataset_name="test2",
            file_path="/test/path/2",
            filetype="cooler",
            processing_state="finished",
            user_id=2,
        )
        # add owned bedfile
        self.owned_bedfile = Dataset(
            id=4,
            dataset_name="test3",
            file_path="/test/path/3",
            filetype="bedfile",
            processing_state="finished",
            user_id=1,
        )
        # add public bedfile
        self.public_bedfile = Dataset(
            dataset_name="test4",
            file_path="/test/path/4",
            filetype="bedfile",
            processing_state="finished",
            public=True,
            user_id=2,
        )
        # add unowned bedfile
        self.unowned_bedfile = Dataset(
            id=5,
            dataset_name="test4",
            file_path="/test/path/4",
            filetype="bedfile",
            processing_state="finished",
            user_id=2,
        )
        # define session that contains unwoned bedfile
        self.session_unowned_cooler = Session(datasets=[self.unowned_cooler])
        # aggregated datasets
        self.owned_coolers = [self.owned_cooler_1, self.owned_cooler_2]
        self.owned_datasets = [*self.owned_coolers, self.owned_bedfile]
        self.all_datasets = [
            *self.owned_datasets,
            self.unowned_bedfile,
            self.unowned_cooler,
        ]

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
        # add datasets
        db.session.add_all(self.owned_coolers)
        db.session.commit()
        # get datasets
        response = self.client.get(
            "/api/datasets/cooler",
            headers=token_headers,
            content_type="application/json",
        )
        # check response
        self.assertEqual(response.status_code, 200)
        expected = [dataset.to_json() for dataset in self.owned_coolers]
        self.assertEqual(response.json, expected)

    def test_get_bedfiles(self):
        """Authenticated user gets bed datasets."""
        # add new user
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add new datasets
        db.session.add(self.owned_bedfile)
        db.session.commit()
        # get datasets
        response = self.client.get(
            "/api/datasets/bed", headers=token_headers, content_type="application/json"
        )
        # check response
        self.assertEqual(response.status_code, 200)
        expected = [self.owned_bedfile.to_json()]
        self.assertEqual(response.json, expected)

    def test_get_all_datasets(self):
        """Authenticated user gets cooler and bed datasets"""
        # add new user
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add new datasets
        db.session.add_all(self.owned_datasets)
        # get datasets
        response = self.client.get(
            "/api/datasets/", headers=token_headers, content_type="application/json"
        )
        # check response
        self.assertEqual(response.status_code, 200)
        expected = [dataset.to_json() for dataset in self.owned_datasets]
        self.assertEqual(response.json, expected)

    def test_wrong_path(self):
        """Authenticated user tries to get datasets with wrong
        parameters."""
        # add new user
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # get datasets
        response = self.client.get(
            "/api/datasets/asdf", headers=token_headers, content_type="application/json"
        )
        self.assertEqual(response.status_code, 404)

    def test_user_can_get_only_own_datasets(self):
        """Authenticated user can only get own datasets"""
        token1 = self.add_and_authenticate("test", "asdf")
        # add datasets
        db.session.add_all(self.all_datasets)
        db.session.commit()
        # get datasets with user_token 1
        token_headers = self.get_token_header(token1)
        # get datasets
        response = self.client.get(
            "/api/datasets/", headers=token_headers, content_type="application/json"
        )
        # check response
        self.assertEqual(response.status_code, 200)
        expected = [dataset.to_json() for dataset in self.owned_datasets]
        self.assertEqual(response.json, expected)
        # check response for coolers
        response = self.client.get(
            "/api/datasets/cooler",
            headers=token_headers,
            content_type="application/json",
        )
        # check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json, [dataset.to_json() for dataset in self.owned_coolers]
        )
        # check response for bedfiles
        response = self.client.get(
            "/api/datasets/bed", headers=token_headers, content_type="application/json"
        )
        # check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [self.owned_bedfile.to_json()])

    def test_user_can_get_datasets_w_session_token(self):
        """Authenticated user can get datasets that they
        do not own if they have a session token."""
        token1 = self.add_and_authenticate("test", "asdf")
        # add datasets
        db.session.add_all([*self.all_datasets, self.session_unowned_cooler])
        db.session.commit()
        # get datasets using session token
        token_headers = self.get_token_header(token1)
        token = self.session_unowned_cooler.generate_session_token()
        # get datasets with session token
        response = self.client.get(
            f"/api/datasets/?sessionToken={token}",
            headers=token_headers,
            content_type="application/json",
        )
        # check response
        self.assertEqual(response.status_code, 200)
        expected = sorted(
            [
                dataset.to_json()
                for dataset in [*self.owned_datasets, self.unowned_cooler]
            ],
            key=lambda x: x["id"],
        )
        self.assertEqual(sorted(response.json, key=lambda x: x["id"]), expected)

    def test_user_cannot_get_datasets_w_invalid_session_token(self):
        """Authenticated user  cannot get other datasets with
        an invalid sessino token."""
        token1 = self.add_and_authenticate("test", "asdf")
        # add datasets
        db.session.add_all(self.all_datasets)
        db.session.commit()
        # get datasets with user_token 1
        token_headers = self.get_token_header(token1)
        token = "badToken"
        # get datasets with session token
        response = self.client.get(
            f"/api/datasets/?sessionToken={token}",
            headers=token_headers,
            content_type="application/json",
        )
        # check response
        self.assertEqual(response.status_code, 200)
        expected = [dataset.to_json() for dataset in self.owned_datasets]
        self.assertEqual(response.json, expected)

    def test_user_gets_public_dataset(self):
        """Tests whether user is able to access public dataset."""
        token1 = self.add_and_authenticate("test", "asdf")
        # add datasets
        db.session.add_all([*self.all_datasets, self.public_bedfile])
        db.session.commit()
        # get datasets with user_token 1
        token_headers = self.get_token_header(token1)
        # get datasets
        response = self.client.get(
            "/api/datasets/", headers=token_headers, content_type="application/json"
        )
        # check response
        self.assertEqual(response.status_code, 200)
        expected = sorted(
            [
                dataset.to_json()
                for dataset in [*self.owned_datasets, self.public_bedfile]
            ],
            key=lambda x: x["id"],
        )
        self.assertEqual(sorted(response.json, key=lambda x: x["id"]), expected)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
