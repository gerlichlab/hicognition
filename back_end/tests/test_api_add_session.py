import sys
import unittest
from test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
sys.path.append("./")
from app import db
from app.models import Dataset, Session


class TestAddSessionObject(LoginTestCase, TempDirTestCase):
    """Tests whether post routes for sessions works."""

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
            "used_datasets": "[1, 2, 3, 4]"
        }
        # dispatch post request
        response = self.client.post(
            "/api/sessions/",
            content_type="multipart/form-data",
            headers=token_headers,
            data=data
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
            "used_datasets": "[1, 2, 3, 4]"
        }
        # dispatch post request
        response = self.client.post(
            "/api/sessions/",
            content_type="multipart/form-data",
            headers=token_headers,
            data=data
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
            "used_datasets": "[1, 2, 3, 4]"
        }
        # dispatch post request
        response = self.client.post(
            "/api/sessions/",
            content_type="multipart/form-data",
            headers=token_headers,
            data=data
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
            "session_type": "compare"
        }
        # dispatch post request
        response = self.client.post(
            "/api/sessions/",
            content_type="multipart/form-data",
            headers=token_headers,
            data=data
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
            "used_datasets": "[1, 2, 3]"
        }
        # dispatch post request
        response = self.client.post(
            "/api/sessions/",
            content_type="multipart/form-data",
            headers=token_headers,
            data=data
        )
        self.assertEqual(response.status_code, 400)

    def test_session_w_existing_dataset_added_correctly(self):
        """Test whether post request to add a session with a single dataset is 
        processed correctly."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # add dataset
        # add dataset
        dataset = Dataset(id=1, user_id=1)
        db.session.add(dataset)
        db.session.commit()
        data = {
            "name": "test-session",
            "session_object": "test-object",
            "session_type": "compare",
            "used_datasets": "[1]"
        }
        # dispatch post request
        response = self.client.post(
            "/api/sessions/",
            content_type="multipart/form-data",
            headers=token_headers,
            data=data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'session_id': '1'})
        session = Session.query.get(1)
        self.assertTrue(session is not None)
        self.assertEqual(session.datasets, [dataset])

    def test_session_w_unowned_dataset_rejected(self):
        """Test whether post request to add a session with a dataset
        that is not owned is rejected"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # add dataset
        # add dataset
        dataset = Dataset(id=1, user_id=2)
        db.session.add(dataset)
        db.session.commit()
        data = {
            "name": "test-session",
            "session_object": "test-object",
            "session_type": "compare",
            "used_datasets": "[1]"
        }
        # dispatch post request
        response = self.client.post(
            "/api/sessions/",
            content_type="multipart/form-data",
            headers=token_headers,
            data=data
        )
        self.assertEqual(response.status_code, 403)

    def test_session_w_existing_datasets_added_correctly(self):
        """Test whether post request to add a session with a multiple datasets is 
        processed correctly."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # add dataset
        # add dataset
        dataset1 = Dataset(id=1, user_id=1)
        dataset2 = Dataset(id=2, user_id=1)
        db.session.add_all([dataset1, dataset2])
        db.session.commit()
        data = {
            "name": "test-session",
            "session_object": "test-object",
            "session_type": "compare",
            "used_datasets": "[1, 2]"
        }
        # dispatch post request
        response = self.client.post(
            "/api/sessions/",
            content_type="multipart/form-data",
            headers=token_headers,
            data=data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'session_id': '1'})
        session = Session.query.get(1)
        self.assertTrue(session is not None)
        self.assertEqual(session.datasets, [dataset1, dataset2])


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
