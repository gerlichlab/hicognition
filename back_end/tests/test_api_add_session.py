import sys
import unittest
from test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
sys.path.append("./")
from app import db
from app.models import Dataset, Session, Collection


class TestAddSessionObject(LoginTestCase, TempDirTestCase):
    """Tests whether post routes for sessions works."""

    def setUp(self):
        super().setUp()
        # add datasets
        self.empty_owned_dataset_1 = Dataset(id=1, user_id=1)
        self.empty_owned_dataset_2 = Dataset(id=2, user_id=1)
        self.owned_datasets = [self.empty_owned_dataset_1, self.empty_owned_dataset_2]
        self.empty_unowned_dataset = Dataset(id=1, user_id=2)
        self.collection_1 = Collection(
            id=1,
            user_id=1
        )
        self.collection_2 = Collection(
            id=2,
            user_id=2
        )

    def test_access_denied_without_token(self):
        """Test whether post request results in 401 error
        if no token is provided."""
        # dispatch post request
        response = self.client.post(
            "/api/sessions/",
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 401)

    def test_invalid_form_no_form_data(self):
        """Test whether post request without form is rejected."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # dispatch post request
        response = self.client.post(
            "/api/sessions/",
            content_type="multipart/form-data",
            headers=token_headers,
        )
        self.assertEqual(response.status_code, 400)

    def test_invalid_form_no_name(self):
        """Test whether post request without name is rejected."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        data = {
            "session_object": "test-object",
            "session_type": "compare",
            "used_datasets": "[1, 2, 3, 4]",
            "used_collections": "[1,2]"
        }
        # dispatch post request
        response = self.client.post(
            "/api/sessions/",
            content_type="multipart/form-data",
            headers=token_headers,
            data=data,
        )
        self.assertEqual(response.status_code, 400)

    def test_invalid_form_no_session_object(self):
        """Test whether post request without session_object is rejected."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        data = {
            "name": "test-session",
            "session_type": "compare",
            "used_datasets": "[1, 2, 3, 4]",
            "used_collections": "[1,2]"
        }
        # dispatch post request
        response = self.client.post(
            "/api/sessions/",
            content_type="multipart/form-data",
            headers=token_headers,
            data=data,
        )
        self.assertEqual(response.status_code, 400)

    def test_invalid_form_no_session_type(self):
        """Test whether post request without session_type is rejected."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        data = {
            "name": "test-session",
            "session_object": "test-object",
            "used_datasets": "[1, 2, 3, 4]",
            "used_collections": "[1,2]"
        }
        # dispatch post request
        response = self.client.post(
            "/api/sessions/",
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
        data = {
            "name": "test-session",
            "session_object": "test-object",
            "session_type": "compare",
            "used_collections": "[1,2]"
        }
        # dispatch post request
        response = self.client.post(
            "/api/sessions/",
            content_type="multipart/form-data",
            headers=token_headers,
            data=data,
        )
        self.assertEqual(response.status_code, 400)

    def test_invalid_form_no_used_collections(self):
        """Test whether post request without used_datasets is rejected."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        data = {
            "name": "test-session",
            "session_object": "test-object",
            "session_type": "compare",
            "used_datasets": "[1,2]"
        }
        # dispatch post request
        response = self.client.post(
            "/api/sessions/",
            content_type="multipart/form-data",
            headers=token_headers,
            data=data,
        )
        self.assertEqual(response.status_code, 400)

    def test_invalied_from_non_existing_datasets(self):
        """Test whether post request with non-existing datasets is rejected."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        data = {
            "name": "test-session",
            "session_object": "test-object",
            "session_type": "compare",
            "used_datasets": "[1, 2, 3]",
            "used_collections": "[]"
        }
        # dispatch post request
        response = self.client.post(
            "/api/sessions/",
            content_type="multipart/form-data",
            headers=token_headers,
            data=data,
        )
        self.assertEqual(response.status_code, 400)

    def test_invalid_from_non_existing_collections(self):
        """Test whether post request with non-existing datasets is rejected."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        data = {
            "name": "test-session",
            "session_object": "test-object",
            "session_type": "compare",
            "used_datasets": "[]",
            "used_collections": "[1,2]"
        }
        # dispatch post request
        response = self.client.post(
            "/api/sessions/",
            content_type="multipart/form-data",
            headers=token_headers,
            data=data,
        )
        self.assertEqual(response.status_code, 400)

    def test_session_w_unowned_dataset_rejected(self):
        """Test whether post request to add a session with a dataset
        that is not owned is rejected"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # add dataset
        db.session.add(self.empty_unowned_dataset)
        db.session.commit()
        data = {
            "name": "test-session",
            "session_object": "test-object",
            "session_type": "compare",
            "used_datasets": "[1]",
            "used_collections": "[1,2]"
        }
        # dispatch post request
        response = self.client.post(
            "/api/sessions/",
            content_type="multipart/form-data",
            headers=token_headers,
            data=data,
        )
        self.assertEqual(response.status_code, 403)

    def test_session_w_unowned_collections_rejected(self):
        """Test whether post request to add a session with a dataset
        that is not owned is rejected"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # add dataset
        db.session.add(self.collection_2)
        db.session.commit()
        data = {
            "name": "test-session",
            "session_object": "test-object",
            "session_type": "compare",
            "used_datasets": "[]",
            "used_collections": "[2]"
        }
        # dispatch post request
        response = self.client.post(
            "/api/sessions/",
            content_type="multipart/form-data",
            headers=token_headers,
            data=data,
        )
        self.assertEqual(response.status_code, 403)

    def test_session_w_existing_dataset_added_correctly(self):
        """Test whether post request to add a session with a single dataset is
        processed correctly."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # add dataset
        db.session.add(self.empty_owned_dataset_1)
        db.session.commit()
        data = {
            "name": "test-session",
            "session_object": "test-object",
            "session_type": "compare",
            "used_datasets": "[1]",
            "used_collections": "[]"
        }
        # dispatch post request
        response = self.client.post(
            "/api/sessions/",
            content_type="multipart/form-data",
            headers=token_headers,
            data=data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"session_id": "1"})
        session = Session.query.get(1)
        self.assertTrue(session is not None)
        self.assertEqual(session.datasets, [self.empty_owned_dataset_1])
        self.assertEqual(len(session.collections), 0)

    def test_session_w_existing_datasets_and_collections_added_correctly(self):
        """Test whether post request to add a session with multiple datasets is
        processed correctly."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # add dataset
        db.session.add_all(self.owned_datasets)
        db.session.add(self.collection_1)
        db.session.commit()
        data = {
            "name": "test-session",
            "session_object": "test-object",
            "session_type": "compare",
            "used_datasets": "[1, 2]",
            "used_collections": "[1]"
        }
        # dispatch post request
        response = self.client.post(
            "/api/sessions/",
            content_type="multipart/form-data",
            headers=token_headers,
            data=data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"session_id": "1"})
        session = Session.query.get(1)
        self.assertTrue(session is not None)
        self.assertEqual(session.datasets, self.owned_datasets)
        self.assertEqual(session.collections, [self.collection_1])


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
