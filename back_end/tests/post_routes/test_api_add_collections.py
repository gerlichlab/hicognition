"""Module with tests realted adding and managing collections."""

import unittest
from hicognition.test_helpers import LoginTestCase

# add path to import app
# import sys
# sys.path.append("./")
from app import db
from app.models import Dataset, Collection


class TestAddCollection(LoginTestCase):
    """Tests post route for adding collections."""

    def setUp(self):
        super().setUp()
        # add datasets
        self.empty_owned_dataset_1 = Dataset(id=1, user_id=1)
        self.empty_owned_dataset_2 = Dataset(id=2, user_id=1)
        self.owned_datasets = [self.empty_owned_dataset_1, self.empty_owned_dataset_2]
        self.empty_unowned_dataset = Dataset(id=1, user_id=2)

    def test_access_denied_without_token(self):
        """Tests whether post request results in 401 error
        if no token is provided."""
        # dispatch post request
        response = self.client.post(
            "/api/collections/", content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 401)

    def test_invalid_form_no_form_data(self):
        """Test whether post request without form is rejected."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # dispatch post request
        response = self.client.post(
            "/api/collections/",
            content_type="multipart/form-data",
            headers=token_headers,
        )
        self.assertEqual(response.status_code, 400)

    def test_invalid_form_no_name(self):
        """Test whether post request without name is rejected."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        data = {"used_datasets": "[1, 2, 3, 4]", "kind": "regions"}
        # dispatch post request
        response = self.client.post(
            "/api/collections/",
            content_type="multipart/form-data",
            headers=token_headers,
            data=data,
        )
        self.assertEqual(response.status_code, 400)

    def test_invalid_form_no_used_datasets(self):
        """Test whether post request without used_datasets is rejected."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        data = {"name": "test-collection", "kind": "regions"}
        # dispatch post request
        response = self.client.post(
            "/api/collections/",
            content_type="multipart/form-data",
            headers=token_headers,
            data=data,
        )
        self.assertEqual(response.status_code, 400)

    def test_invalid_form_no_collection_kind(self):
        """Test whether post request without used_datasets is rejected."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        data = {"used_datasets": "[1, 2, 3, 4]", "name": "test-collection"}
        # dispatch post request
        response = self.client.post(
            "/api/collections/",
            content_type="multipart/form-data",
            headers=token_headers,
            data=data,
        )
        self.assertEqual(response.status_code, 400)

    def test_invalid_from_non_existing_datasets(self):
        """Test whether post request with non-existing datasets is rejected."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        data = {
            "name": "test-collection",
            "used_datasets": "[1, 2, 3]",
            "kind": "regions",
        }
        # dispatch post request
        response = self.client.post(
            "/api/collections/",
            content_type="multipart/form-data",
            headers=token_headers,
            data=data,
        )
        self.assertEqual(response.status_code, 400)

    def test_collection_w_unowned_dataset_rejected(self):
        """Test whether post request to add a collection with a dataset
        that is not owned is rejected"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # add dataset
        db.session.add(self.empty_unowned_dataset)
        db.session.commit()
        data = {"name": "test-collection", "used_datasets": "[1]", "kind": "regions"}
        # dispatch post request
        response = self.client.post(
            "/api/collections/",
            content_type="multipart/form-data",
            headers=token_headers,
            data=data,
        )
        self.assertEqual(response.status_code, 403)

    def test_collection_w_existing_datasets_added_correctly(self):
        """Test whether post request to add a collection with multiple datasets is
        processed correctly."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # add dataset
        db.session.add_all(self.owned_datasets)
        db.session.commit()
        data = {"name": "test-collection", "used_datasets": "[1, 2]", "kind": "regions"}
        # dispatch post request
        response = self.client.post(
            "/api/collections/",
            content_type="multipart/form-data",
            headers=token_headers,
            data=data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"collection_id": "1"})
        collection = Collection.query.get(1)
        self.assertTrue(collection is not None)
        self.assertEqual(collection.datasets, self.owned_datasets)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
