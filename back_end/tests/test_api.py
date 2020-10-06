from test_helpers import LoginTest
from app import create_app, db
from app.models import User, Dataset


class TestAuth(LoginTest):
    """Tests api-authentication"""

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


class TestGetDatasets(LoginTest):
    """Tests for /api/datasets route to list
    datasets."""

    def add_test_datasets(self):
        """adds test datasets to db"""
        dataset1 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            higlass_uuid="asdf1234",
            filetype="cooler",
        )
        dataset2 = Dataset(
            dataset_name="test2",
            file_path="/test/path/2",
            higlass_uuid="fdsa4321",
            filetype="cooler",
        )
        dataset3 = Dataset(
            dataset_name="test3",
            file_path="/test/path/3",
            higlass_uuid="fdsa8765",
            filetype="bedfile",
        )
        db.session.add(dataset1)
        db.session.add(dataset2)
        db.session.add(dataset3)
        db.session.commit()

    def add_and_authenticate(self, username, password):
        """adds a user with username and password, authenticates
        the user and returns a token."""
         # add new user
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        # get token
        headers = self.get_api_headers("test", "asdf")
        response = self.client.post(
            "/api/tokens/", headers=headers, content_type="application/json"
        )
        return response.get_json()["token"]

    def test_no_auth(self):
        """No authentication provided, response should be 401"""
        # protected route
        response = self.client.get("/api/datasets/", content_type="application/json")
        self.assertEqual(response.status_code, 401)

    def test_get_coolers(self):
        """Authenticated user gets some datasets."""
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
            },
            {
                "dataset_name": "test2",
                "file_path": "/test/path/2",
                "filetype": "cooler",
                "higlass_uuid": "fdsa4321",
                "id": 2,
            },
        ]
        self.assertEqual(response.json, expected)

    def test_get_bedfiles(self):
        """Authenticated user gets some datasets."""
        # add new user
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add new datasets
        self.add_test_datasets()
        # get datasets
        response = self.client.get(
            "/api/datasets/bed",
            headers=token_headers,
            content_type="application/json",
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
            },
        ]
        self.assertEqual(response.json, expected)