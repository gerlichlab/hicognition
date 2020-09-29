import unittest
from base64 import b64encode
from app import create_app, db
from app.models import User


class TestAuth(unittest.TestCase):
    """Tests api-authentication"""

    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_api_headers(self, username, password):
        return {
            "Authorization": "Basic "
            + b64encode((username + ":" + password).encode("utf-8")).decode("utf-8"),
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def get_token_header(self, token):
        return {
            "Authorization": "Basic "
            + b64encode((token + ":").encode("utf-8")).decode("utf-8"),
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def test_no_auth_allowed(self):
        """tests whether unprotected routes can be
        accessed as expected."""
        # unprotected route
        response = self.client.get("/api/test", content_type="application/json")
        self.assertEqual(response.status_code, 200)

    def test_no_auth_not_allowed(self):
        """tests whether protected routes cannot be
        accessed when not authentication is presented"""
        # protected route
        response = self.client.get(
            "/api/testProtected", content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

    def test_password_auth(self):
        """test whether user with password can get protected
        and unprotected content"""
        # add new user
        new_user = User(username="test")
        new_user.set_password("asdf")
        db.session.add(new_user)
        db.session.commit()
        # test authentication for protected routes
        headers = self.get_api_headers("test", "asdf")
        response = self.client.get(
            "/api/testProtected", headers=headers, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        # test authentication for unprotected routes
        response = self.client.get(
            "/api/test", headers=headers, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

    def test_token_auth(self):
        """tests whether obtained token can be used
        for authentication."""
        # add new user
        new_user = User(username="test")
        new_user.set_password("asdf")
        db.session.add(new_user)
        db.session.commit()
        # get token
        headers = self.get_api_headers("test", "asdf")
        response = self.client.post(
            "/api/tokens/", headers=headers, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        token = response.get_json()["token"]
        # create token header
        token_headers = self.get_token_header(token)
        # test whether token can be used for authentication
        response = self.client.get(
            "/api/testProtected", headers=token_headers, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

    def test_no_new_token_with_token(self):
        """test that one cannot get a new token with the old token"""
        # add new user
        new_user = User(username="test")
        new_user.set_password("asdf")
        db.session.add(new_user)
        db.session.commit()
        # get token
        headers = self.get_api_headers("test", "asdf")
        response = self.client.post(
            "/api/tokens/", headers=headers, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        token = response.get_json()["token"]
        # create token header
        token_headers = self.get_token_header(token)
        # test whether token can be used for authentication
        response = self.client.post(
            "/api/tokens/", headers=token_headers, content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)
