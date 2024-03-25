"""Generate and check email confirmation tokens"""
from flask import render_template
from flask_mail import Message

from itsdangerous import URLSafeTimedSerializer


class ConfirmationHandler:
    """Responsible for generating and checking confirmation tokens"""

    def __init__(self, mail_client, secret_key=None, secret_salt=None) -> None:
        self._secret_key = secret_key
        self._secret_salt = secret_salt
        self._mail_client = mail_client

    def init_app(self, app):
        self._secret_key = app.config["SECRET_KEY"]
        self._secret_salt = app.config["SECRET_SALT"]

    def _generate_confirmation_token(self, email):
        serializer = URLSafeTimedSerializer(self._secret_key)
        return serializer.dumps(email, salt=self._secret_salt)

    def _generate_confirmation_url(self, base_url, email):
        return (
            base_url
            + "/#/confirmEmail?emailToken="
            + self._generate_confirmation_token(email)
        )

    def generate_confirmation_email(self, base_url, email):
        return render_template(
            "confirmation_email.html",
            confirm_url=self._generate_confirmation_url(base_url, email),
        )

    def confirm_token(self, token, expiration=3600):
        serializer = URLSafeTimedSerializer(self._secret_key)
        try:
            email = serializer.loads(token, salt=self._secret_salt, max_age=expiration)
        except:
            return False
        return email

    def send_confirmation_mail(self, base_url, email):
        """"""
        html_template = self.generate_confirmation_email(base_url, email)
        msg = Message(
            html=html_template, subject="Confirm your email", recipients=[email]
        )
        self._mail_client.send(msg)
