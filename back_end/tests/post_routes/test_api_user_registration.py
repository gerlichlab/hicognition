"""Tests user registration"""
import unittest
from hicognition.test_helpers import LoginTestCase
from werkzeug.security import check_password_hash

from app import db
from app.models import User


class TestUserRegistration(LoginTestCase):


    def test_form_validation(self):
        """Tests whether form is validated
        correctly."""

        test_cases = {
            "no_form": {
                "data": None,
                "status_code": 400,
                "msg": "Form is not valid"
            },
            "form_without_user_name": {
                "data": {
                    "email_address": "test@test.at",
                    "password": "test"
                },
                "status_code": 400,
                "msg": "Form is not valid"
            },
            "form_without_email": {
                "data": {
                    "user_name": "test",
                    "password": "Test"
                },
                "status_code": 400,
                "msg": "Form is not valid"
            },
            "form_without_password": {
                "data": {
                    "user_name": "test",
                    "email_address": "test@test.at"
                },
                "status_code": 400,
                "msg": "Form is not valid"
            },
            "valid_form": {
                "data": {
                    "user_name": "test",
                    "password": "test12345",
                    "email_address": "test@test.at"
                },
                "status_code": 200,
                "msg": "Registration successful"
            }
        }

        for key, test_case in test_cases.items():
            with self.subTest(key=key):
                response = self.client.post(
                    "/api/register/",
                    data=test_case['data'],
                    content_type="multipart/form-data",
                )
                self.assertEqual(response.status_code, test_case['status_code'])
                # check message
                response_data = response.get_json()
                self.assertTrue(test_case["msg"] in response_data["message"]) 

    def test_duplicate_user_is_rejected(self):
        """Tests whether a duplicate user name is rejected"""
        # test cases
        test_cases = {
            "duplicate_name": {
                "data": {
                    "user_name": "test",
                    "email_address": "test2@test.at",
                    "password": "test1234"
                },
                "status_code": 400,
                "msg": "User with this name or email address already exists!"
            },
            "duplicate_mail_address": {
                "data": {
                    "user_name": "test2",
                    "email_address": "test@test.at",
                    "password": "test1234"
                },
                "status_code": 400,
                "msg": "User with this name or email address already exists!"
            }
        }
        # setup
        user = User(username="test", email="test@test.at")
        db.session.add(user)
        db.session.commit()
        # dispatch
        for key, test_case in test_cases.items():
            with self.subTest(key=key):
                response = self.client.post(
                    "/api/register/",
                    data=test_case['data'],
                    content_type="multipart/form-data",
                )
                self.assertEqual(response.status_code, test_case['status_code'])
                # check message
                response_data = response.get_json()
                self.assertTrue(test_case["msg"] in response_data["message"])

    def test_successful_registration(self):
        self.client.post(
                "/api/register/",
                data={
                    "user_name": "test",
                    "password": "test12345",
                    "email_address": "test@test.at"
                },
                content_type="multipart/form-data",
            )
        # check whether user has been created successfully and confirmed flag was set to False
        self.assertEqual(len(User.query.all()), 1)
        u = User.query.all()[0]
        self.assertEqual(u.username, 'test')
        self.assertEqual(u.email, 'test@test.at')
        self.assertTrue(check_password_hash(u.password_hash, 'test12345'))
        self.assertEqual(u.email_confirmed, False)



if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
