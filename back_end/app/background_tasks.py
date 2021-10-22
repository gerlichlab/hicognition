"""Background tasks"""
from flask.globals import current_app
from .models import User, Task
from . import db


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


def cleanup_empty_tasks():
    """Cleans up tasks that are not conneced to a redis job anymore."""
    tasks = Task.query.all()
    deletion_number = 0
    for task in tasks:
        if task.get_rq_job() is None:
            deletion_number += 1
            db.session.delete(task)
    current_app.logger.info(f"Background process deleted {deletion_number} tasks")
    db.session.commit()