import unittest
from unittest.mock import patch
from test_helpers import LoginTestCase

# add path to import app
import sys

sys.path.append("./")
from app import db
from app.models import Collection, Dataset, Session, Task


class TestGetCollections(LoginTestCase):
    """Tests for /api/collections/ route to list collections."""

    def setUp(self):
        super().setUp()
        # define datasets
        self.owned_dataset_1 = Dataset(dataset_name="test1")
        self.owned_dataset_2 = Dataset(dataset_name="test2")
        # define collections
        self.collection_user_1 = Collection(
            user_id=1,
            name="test",
            datasets=[self.owned_dataset_1, self.owned_dataset_2],
        )
        self.collection_user_1_2 = Collection(
            user_id=1,
            name="test2",
            datasets=[self.owned_dataset_1, self.owned_dataset_2],
        )
        self.collection_user_2 = Collection(
            user_id=2,
            name="test3",
            datasets=[self.owned_dataset_1, self.owned_dataset_2],
        )
        # add public collection
        self.public_collection = Collection(
            name="test4",
            user_id=2,
            public=True,
            datasets=[self.owned_dataset_1, self.owned_dataset_2],
        )
        # define session that contains unowned collection
        self.session_unowned_collection = Session(collections=[self.collection_user_2])

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

    def test_user_can_get_collection_w_session_token(self):
        """Authenticated user can get datasets that they
        do not own if they have a session token."""
        token1 = self.add_and_authenticate("test", "asdf")
        # add datasets
        db.session.add_all([self.collection_user_2, self.session_unowned_collection])
        db.session.commit()
        # get datasets using session token
        token_headers = self.get_token_header(token1)
        token = self.session_unowned_collection.generate_session_token()
        # get datasets with session token
        response = self.client.get(
            f"/api/collections/?sessionToken={token}",
            headers=token_headers,
            content_type="application/json",
        )
        # check response
        self.assertEqual(response.status_code, 200)
        expected = [
            collection.to_json()
            for collection in self.session_unowned_collection.collections
        ]
        self.assertEqual(response.json, expected)

    def test_user_cannot_get_collection_w_invalid_session_token(self):
        """Authenticated user  cannot get other collections with
        an invalid sessino token."""
        token1 = self.add_and_authenticate("test", "asdf")
        # add datasets
        db.session.add_all([self.collection_user_2, self.session_unowned_collection])
        db.session.commit()
        # get datasets with user_token 1
        token_headers = self.get_token_header(token1)
        token = "badToken"
        # get datasets with session token
        response = self.client.get(
            f"/api/collections/?sessionToken={token}",
            headers=token_headers,
            content_type="application/json",
        )
        # check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])


class TestProcessingStateIsUpdated(LoginTestCase):
    """Tests whether get route updates processing state"""

    def setUp(self):
        """adds test datasets to db"""
        super().setUp()
        # add finished dataset
        self.finished_collection = Collection(
            id=1,
            processing_state="finished",
            user_id=1,
        )
        # add processing dataset
        self.processing_collection = Collection(
            id=2,
            processing_state="processing",
            user_id=1,
        )
        # add uploading dataset
        self.uploading_collection = Collection(
            id=3,
            processing_state="uploading",
            user_id=1,
        )

    @patch("app.models.any_tasks_failed")
    @patch("app.models.all_tasks_finished")
    def test_processing_when_task(self, mock_finished, mock_failed):
        """Tests whether processing status is set correctly
        when there is a running task for collections."""
        # set return value of mock_finished and mock_failed
        mock_finished.return_value = False
        mock_failed.return_value = False
        # add new user
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add collection and task
        db.session.add(self.finished_collection)
        db.session.add(Task(id="asdf", collection_id=self.finished_collection.id))
        db.session.commit()
        # get collection
        response = self.client.get(
            "/api/collections/",
            headers=token_headers,
            content_type="application/json",
        )
        # check response
        self.assertEqual(response.status_code, 200)
        collection = Collection.query.get(self.finished_collection.id)
        self.assertEqual(collection.processing_state, "processing")

    def test_finished_when_no_task(self):
        """Tests whether collection is swithced from processing to finished if there is no task"""
        # add new user
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add new collections
        db.session.add_all([self.processing_collection])
        db.session.commit()
        # get collection
        response = self.client.get(
            "/api/collections/",
            headers=token_headers,
            content_type="application/json",
        )
        # check response
        self.assertEqual(response.status_code, 200)
        collection = Collection.query.get(self.processing_collection.id)
        self.assertEqual(collection.processing_state, "finished")

    def test_uploading_dataset_no_update_wo_task(self):
        # add new user
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add new collections
        db.session.add_all([self.uploading_collection])
        db.session.commit()
        # get collections
        response = self.client.get(
            "/api/collections/",
            headers=token_headers,
            content_type="application/json",
        )
        # check response
        self.assertEqual(response.status_code, 200)
        collection = Collection.query.get(self.uploading_collection.id)
        self.assertEqual(collection.processing_state, "uploading")

    def test_uploading_dataset_no_update_w_task(self):
        # add new user
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add new collections
        db.session.add_all(
            [
                self.uploading_collection,
                Task(id="asdf", collection_id=self.uploading_collection.id),
            ]
        )
        db.session.commit()
        # get collection
        response = self.client.get(
            "/api/collections/",
            headers=token_headers,
            content_type="application/json",
        )
        # check response
        self.assertEqual(response.status_code, 200)
        collection = Collection.query.get(self.uploading_collection.id)
        self.assertEqual(collection.processing_state, "uploading")


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
