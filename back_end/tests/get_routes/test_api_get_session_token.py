import datetime
import unittest
from hicognition.test_helpers import LoginTestCase

# add path to import app
import sys

sys.path.append("./")
from app import db
from app.models import Dataset, Task, Session


class TestGetSessionToken(LoginTestCase):
    """Tests for /api/sessions/id/sessionToken route to list
    datasets."""

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
        response = self.client.get(
            "/api/sessions/1/sessionToken/", content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

    def test_session_does_not_exist(self):
        """Session with id 500 does not exist"""
        token = self.add_and_authenticate("test", "asdf")
        # create token_headers
        token_headers = self.get_token_header(token)
        # by user id 2
        response = self.client.get(
            "/api/sessions/500/sessionToken/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_unowned_session(self):
        """Existing session is not owned."""
        token = self.add_and_authenticate("test", "asdf")
        # create token_headers
        token_headers = self.get_token_header(token)
        # add session
        db.session.add(self.session_user_2)
        db.session.commit()
        # by user id 2
        response = self.client.get(
            "/api/sessions/1/sessionToken/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_valid_token_for_owned_session(self):
        """Existing session is not owned."""
        token = self.add_and_authenticate("test", "asdf")
        # create token_headers
        token_headers = self.get_token_header(token)
        # add session
        db.session.add_all([self.session_user_1, self.session_user_1_2])
        db.session.commit()
        # by user id 1
        response = self.client.get(
            "/api/sessions/1/sessionToken/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        token = response.json["session_token"]
        # test whether token is valid
        result = Session.verify_auth_token(token)
        self.assertEqual(result, self.session_user_1)

    def test_invalid_token_not_accepted(self):
        """Invalid token is not accepted by session"""
        result = Session.verify_auth_token("asdf")
        self.assertTrue(result is None)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
