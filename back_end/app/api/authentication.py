from flask.json import jsonify
from flask_httpauth import HTTPBasicAuth
from flask import g, request
from . import api
from . import errors
from ..models import User, Session


auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username_or_token, password):
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
    if g.current_user.is_anonymous or g.token_used:
        return errors.forbidden("Invalid credentials")
    return jsonify(
        {
            "token": g.current_user.generate_auth_token(expiration=3600),
            "expiration": 3600,
            "user_id": g.current_user.id,
        }
    )

@api.before_request
def before_request():
    _verify_and_store_session_token(request)



# helpers
def _verify_and_store_session_token(request):
    g.session_datasets = []
    g.session_id = None
    session_token = request.args.get('sessionToken')
    if session_token is None:
        return None
    # check whether session token is valid
    session = Session.verify_auth_token(session_token)
    if session is not None:
        g.session_datasets.extend([dataset.id for dataset in session.datasets])
        g.session_id = session.id