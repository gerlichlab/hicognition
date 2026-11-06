"""Tests the passwords of the User model."""

import unittest

from app.models import User
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

    def test_hash_from_before_werkzeug_3_is_checked(self):
        user = User(username="test", password_hash=OLD_HASH)
        self.assertTrue(user.check_password("reference-password"))
        self.assertFalse(user.check_password("other"))


if __name__ == "__main__":
    unittest.main()
