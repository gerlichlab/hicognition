"""Generate and check email confirmation tokens"""
from flask import render_template

from itsdangerous import URLSafeTimedSerializer


class ConfirmationHandler():
    """Responsible for generating and checking confirmation tokens"""

    def __init__(self, mail_client, secret_key=None, secret_salt=None) -> None:
        self._secret_key = secret_key
        self._secret_salt = secret_salt
        self._mail_client

    def init_app(self, app):
        self._secret_key = app.config['SECRET_KEY']
        self._secret_salt = app.config['SECRET_SALT']

    def _generate_confirmation_token(self, email):
        serializer = URLSafeTimedSerializer(self._secret_key)
        return serializer.dumps(email, salt=self._secret_salt)

    def _generate_confirmation_url(self, email):
        """TODO"""

    def confirm_token(self, token, expiration=3600):
        serializer = URLSafeTimedSerializer(self._secret_key)
        try:
            email = serializer.loads(
                token,
                salt=self._secret_salt,
                max_age=expiration
            )
        except:
            return False
        return email
   
    def send_confirmation_mail(self, email, sender, subject):
        """"""
        # TODO: server needs to know own url
        html_template = render_template("templates/confirmation_email.html", self._generate_confirmation_url(email))