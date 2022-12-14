""" Authenticating credentials of a request and dealing with the tokens. """
from functools import wraps
from flask import g, request, current_app
from flask.json import jsonify
from flask_httpauth import HTTPBasicAuth
from sqlalchemy.exc import IntegrityError
from . import api
from . import errors
from ..form_models import UserRegistrationModel
from ..models import User, Session
from .. import confirmation_handler
from .. import db


auth = HTTPBasicAuth()


class ShowCaseUser:
    def __init__(self):
        self.id = None
        self.is_anonymous = False
        self.email_confirmed = True

    def generate_auth_token(self, expiration):
        return "ASDF"


@auth.verify_password
def verify_password(username_or_token, password):
    """Verifies the password of a user or if a valid token is used."""
    if current_app.config["SHOWCASE"]:
        g.current_user = ShowCaseUser()
        g.token_used = False
        return True
    if username_or_token == "":
        return False
    if password == "":
        g.current_user = User.verify_auth_token(username_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(username=username_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.check_password(password)


@api.route("/tokens/", methods=["POST"])
@auth.login_required
def get_token():
    """Returns a token for a logged-in user."""
    if g.current_user.is_anonymous or g.token_used:
        return errors.forbidden("Invalid credentials")
    if User.query.get(g.current_user.id) is None:
        user_name = "Anonymous"
    else:
        user_name = User.query.get(g.current_user.id).username
    return jsonify(
        {
            "token": g.current_user.generate_auth_token(expiration=3600 * 24),
            "expiration": 3600 * 24,
            "user_id": g.current_user.id,
            "user_name": user_name,
        }
    )


@api.route('/register/', methods=['POST'])
def register():
    if not hasattr(request, "form"):
        return errors.invalid("Request does not contain a form!")
    # get data from form
    try:
        data = UserRegistrationModel(**request.form)
    except ValueError as err:
        return errors.invalid(f'Form is not valid: {str(err)}')
    except Exception as err:
        return errors.internal_server_error(
            err,
            "Registration could not be performed: There was a server-side problem. Error has been logged.",
        )
    # create user
    try:
        user = User(username=data.user_name, email=data.email_address)
        user.set_password(data.password)
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return errors.invalid('User with this name or email address already exists!')
    # send confirmation email
    try:
        confirmation_handler.send_confirmation_mail(request.base_url.split("/register/")[0], data.email_address)
    except BaseException as e:
        current_app.logger.info('Confirmation sending failed!')
        current_app.logger.error(e)
        return errors.internal_server_error(e, "Sending mail failed!")
    return jsonify({"message": "Registration successful"})

@api.route('/resend/', methods=['GET'])
@auth.login_required
def resend_confirmation_mail():
    # send confirmation email
    try:
        confirmation_handler.send_confirmation_mail(request.base_url.split("/resend/")[0], g.current_user.email)
    except BaseException as e:
        current_app.logger.info('Confirmation sending failed!')
        current_app.logger.error(e)
        return errors.internal_server_error(e, "Sending mail failed!")
    return jsonify({"message": "Registration mail resend successfully"})


@api.route('/confirmation/<token>/', methods=['GET'])
@auth.login_required
def confirm_email(token):
    # check if token is ok
    email = confirmation_handler.confirm_token(token)
    if not email:
        return errors.forbidden("Token wrong or expired.")
    # check if email matches
    if not (g.current_user.email == email):
        return errors.forbidden("Wrong email address.")
    # set confirmation state
    g.current_user.email_confirmed = True
    db.session.add(g.current_user)
    db.session.commit()
    return jsonify({"message": "Confirmation successful!"})


def check_confirmed(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if g.current_user.email_confirmed is not True:
            return errors.forbidden("Unconfirmed")
        return func(*args, **kwargs)

    return decorated_function


@api.before_request
def before_request():
    "Gets and stores the session token."
    _verify_and_store_session_token(request)


# helpers
def _verify_and_store_session_token(request):
    """Verifies and stores the session token, in the application context."""
    g.session_datasets = []
    g.session_collections = []
    g.session_id = None
    session_token = request.args.get("sessionToken")
    if session_token is None:
        return None
    # check whether session token is valid
    session = Session.verify_auth_token(session_token)
    if session is not None:
        g.session_datasets.extend([dataset.id for dataset in session.datasets])
        g.session_collections.extend(
            [collection.id for collection in session.collections]
        )
        g.session_id = session.id
