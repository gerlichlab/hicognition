"""Background tasks"""
from flask.globals import current_app
from .models import User


def add_app_context(app):
    def decorated(func):
        def wrapper(*args, **kwargs):
            with app.app_context():
                return func(*args, **kwargs)
        return wrapper   
    return decorated


def test():
    """ Function for test purposes. """
    current_app.logger.info("Scheduler is alive")
    number_users = len(User.query.all())
    current_app.logger.info(f"There are {number_users} users")