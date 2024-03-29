"""Tests for deletion of sessions."""
import datetime
import unittest
from tests.test_utils.test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
# import sys
# sys.path.append("./")
from app import db
from app.models import Session


class TestDeleteSession(LoginTestCase, TempDirTestCase):
    """Tests for deletion of sessions."""

    def setUp(self):
        super().setUp()
        # define datasets
        self.timestamp = datetime.datetime.utcnow()
        self.session_user_1 = Session(
            user_id=1, name="test", created_utc=self.timestamp
        )
        self.session_user_1_2 = Session(
            user_id=1, name="test2", created_utc=self.timestamp
        )
        self.session_user_2 = Session(
            user_id=2, name="test3", created_utc=self.timestamp
        )

    def test_no_auth(self):
        """No authentication provided, response should be 401"""
        # protected route
        response = self.client.delete(
            "/api/sessions/1/", content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

    def test_delete_wo_session_id(self):
        """Should return 405 since delete is not allowed for /api/sessions"""
        response = self.client.delete("/api/sessions/", content_type="application/json")
        self.assertEqual(response.status_code, 405)

    def test_delete_session_does_not_exist(self):
        """test deletion of data set that does not exist."""
        token = self.add_and_authenticate("test", "asdf")
        # create token_headers
        token_headers = self.get_token_header(token)
        # by user id 2
        response = self.client.delete(
            "/api/sessions/500/", headers=token_headers, content_type="application/json"
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_session_wo_permission(self):
        """Should return 403 since dataset is not owned."""
        token = self.add_and_authenticate("test", "asdf")
        # create token_headers
        token_headers = self.get_token_header(token)
        # add session
        db.session.add(self.session_user_2)
        db.session.commit()
        # by user id 2
        response = self.client.delete(
            "/api/sessions/1/", headers=token_headers, content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_owned_session(self):
        """Check whether owned dataset is deleted correctly."""
        token = self.add_and_authenticate("test", "asdf")
        # create token_headers
        token_headers = self.get_token_header(token)
        # add session
        db.session.add_all([self.session_user_1, self.session_user_1_2])
        db.session.commit()
        # by user id 2
        response = self.client.delete(
            "/api/sessions/1/", headers=token_headers, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(Session.query.all()), 1)
        self.assertEqual(Session.query.first(), self.session_user_1_2)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
