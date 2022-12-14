import logging
from flask_httpauth import HTTPBasicAuth
from flask import g
from ..services.user import UserAuthenticationException, user_service
auth = HTTPBasicAuth()

@auth.verify_password
def login(username, password):
    if auth.current_user():
        pass
    try:
        user = user_service.get_user(username, password)
    except UserAuthenticationException as e:
        logging.info(f"Failed login w/ {username} and {password}")
        return False
    #auth.current_user = user
    print(user)
    return user is not None