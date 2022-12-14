"""Tests user registration"""
import unittest
from unittest.mock import patch, MagicMock
from flask import render_template
from flask_mail import Message
from hicognition.test_helpers import LoginTestCase
from werkzeug.security import check_password_hash
from app.confirmation import ConfirmationHandler

from app import db, confirmation_handler
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
            "form_without_userName": {
                "data": {
                    "emailAddress": "test@test.at",
                    "password1": "test"
                },
                "status_code": 400,
                "msg": "Form is not valid"
            },
            "form_without_email": {
                "data": {
                    "userName": "test",
                    "password1": "Test"
                },
                "status_code": 400,
                "msg": "Form is not valid"
            },
            "form_without_password": {
                "data": {
                    "userName": "test",
                    "emailAddress": "test@test.at"
                },
                "status_code": 400,
                "msg": "Form is not valid"
            },
            "valid_form": {
                "data": {
                    "userName": "test",
                    "password1": "test12345",
                    "emailAddress": "test@test.at"
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
                    "userName": "test",
                    "emailAddress": "test2@test.at",
                    "password1": "test1234"
                },
                "status_code": 400,
                "msg": "User with this name or email address already exists!"
            },
            "duplicate_mail_address": {
                "data": {
                    "userName": "test2",
                    "emailAddress": "test@test.at",
                    "password1": "test1234"
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
                    "userName": "test",
                    "password1": "test12345",
                    "emailAddress": "test@test.at"
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


class TestConfirmationEmail(LoginTestCase):
    """Tests that test sending of confirmation email"""

    def test_email_sending_called_correctly(self):
        # mock send method
        confirmation_handler._mail_client.send = MagicMock()
        # dispatch api call
        response = self.client.post(
                "/api/register/",
                data={
                    "userName": "test",
                    "password1": "test12345",
                    "emailAddress": "test@test.at"
                },
                content_type="multipart/form-data",
            )
        # check whether email has been sent correctly
        msg = Message(
            html=confirmation_handler.generate_confirmation_email("http://localhost/api","test@test.at"),
            subject="Confirm your email",
            recipients=["test@test.at"]
        )
        # compare calls; flask mail messages cannot be compared directly
        actual = confirmation_handler._mail_client.send.mock_calls[0].args[0]
        self.assertEqual(msg.html, actual.html)
        self.assertEqual(msg.subject, actual.subject)
        self.assertEqual(msg.recipients, actual.recipients)

if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
