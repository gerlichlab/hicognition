"""Tests the passwords of the User model."""

import unittest

from app import db
from app.models import PASSWORD_HASH_METHOD, User
from tests.test_utils.test_helpers import LoginTestCase

# written by Werkzeug 1.0.1, which HiCognition used until v0.8.0
OLD_HASH = "pbkdf2:sha256:150000$uWWUnCc4$100b642d8899ed17d2d566a124275f5644b2053834f42133492ec4db9099520c"


class TestUserPassword(LoginTestCase):
    def test_hash_fits_the_column(self):
        """MySQL refuses a hash longer than the column; the tests' SQLite doesn't check."""
        user = User(username="test")
        user.set_password("a password of some length, 1234567890")
        self.assertLessEqual(len(user.password_hash), User.password_hash.type.length)

    def test_password_is_checked(self):
        user = User(username="test")
        user.set_password("secret")
        self.assertTrue(user.check_password("secret"))
        self.assertFalse(user.check_password("other"))

    def test_new_hash_uses_the_current_settings(self):
        user = User(username="test")
        user.set_password("secret")
        self.assertTrue(user.password_hash.startswith(PASSWORD_HASH_METHOD + "$"))
        self.assertFalse(user.password_needs_rehash())

    def test_hash_from_before_werkzeug_3_is_checked(self):
        user = User(username="test", password_hash=OLD_HASH)
        self.assertTrue(user.check_password("reference-password"))
        self.assertFalse(user.check_password("other"))
        self.assertTrue(user.password_needs_rehash())

    def test_login_replaces_a_hash_from_before(self):
        db.session.add(User(username="old", password_hash=OLD_HASH))
        db.session.commit()
        response = self.client.post(
            "/api/tokens/",
            headers=self.get_api_headers("old", "reference-password"),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        user = User.query.filter_by(username="old").first()
        self.assertTrue(user.password_hash.startswith(PASSWORD_HASH_METHOD + "$"))
        self.assertTrue(user.check_password("reference-password"))

    def test_failed_login_keeps_the_hash(self):
        db.session.add(User(username="old", password_hash=OLD_HASH))
        db.session.commit()
        response = self.client.post(
            "/api/tokens/",
            headers=self.get_api_headers("old", "wrong password"),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)
        user = User.query.filter_by(username="old").first()
        self.assertEqual(user.password_hash, OLD_HASH)


if __name__ == "__main__":
    unittest.main()
