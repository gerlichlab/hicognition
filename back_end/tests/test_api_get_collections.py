import unittest
from test_helpers import LoginTestCase

# add path to import app
import sys

sys.path.append("./")
from app import db
from app.models import Collection, Dataset



class TestGetCollections(LoginTestCase):
    """Tests for /api/collections/ route to list collections."""

    def setUp(self):
        super().setUp()
        # define datasets
        self.owned_dataset_1 = Dataset(dataset_name="test1")
        self.owned_dataset_2 = Dataset(dataset_name="test2")
        # define collections
        self.collection_user_1 = Collection(
            user_id=1, name="test", datasets=[self.owned_dataset_1, self.owned_dataset_2])
        self.collection_user_1_2 = Collection(
            user_id=1, name="test2", datasets=[self.owned_dataset_1, self.owned_dataset_2])
        self.collection_user_2 = Collection(
            user_id=2, name="test3", datasets=[self.owned_dataset_1, self.owned_dataset_2])
        # add public collection
        self.public_collection = Collection(
            name="test4",
            user_id=2,
            public=True,
            datasets=[self.owned_dataset_1, self.owned_dataset_2]
        )

    def test_no_auth(self):
        """No authentication provided, response should be 401"""
        # protected route
        response = self.client.get("/api/collections/", content_type="application/json")
        self.assertEqual(response.status_code, 401)

    def test_no_collections_returns_empty(self):
        """No collections exist, return value is empty"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # get collections
        response = self.client.get(
            "/api/collections/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json) == 0)

    def test_single_owned_collection_is_returned_correctly(self):
        """Single owned collection is returned correctly"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add session data
        db.session.add(self.collection_user_1)
        db.session.commit()
        # get collections
        response = self.client.get(
            "/api/collections/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [self.collection_user_1.to_json()])

    def test_multiple_owned_collections_are_returned_correctly(self):
        """Multiple owned collections is returned correctly"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add session data
        db.session.add_all([self.collection_user_1, self.collection_user_1_2])
        db.session.commit()
        # get collections
        response = self.client.get(
            "/api/collections/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json,
            [self.collection_user_1.to_json(), self.collection_user_1_2.to_json()],
        )

    def test_only_owned_collections_are_returned(self):
        """Only owned collections are returned"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add session data
        db.session.add_all([self.collection_user_1, self.collection_user_2])
        db.session.commit()
        # get sessions
        response = self.client.get(
            "/api/collections/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [self.collection_user_1.to_json()])

    def test_user_gets_public_collection(self):
        """Tests whether user is able to access public collection."""
        token1 = self.add_and_authenticate("test", "asdf")
        # add datasets
        db.session.add(self.public_collection)
        db.session.commit()
        # get datasets with user_token 1
        token_headers = self.get_token_header(token1)
        # get datasets
        response = self.client.get(
            "/api/collections/",
            headers=token_headers,
            content_type="application/json",
        )
        # check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [self.public_collection.to_json()])


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
