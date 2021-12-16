"""Background tasks"""
from flask.globals import current_app
from .pipeline_steps import set_dataset_failed, set_collection_failed
from .models import Task
from . import db
from .notifications import NotificationHandler


def add_app_context(app):
    def decorated(func):
        def wrapper(*args, **kwargs):
            with app.app_context():
                return func(*args, **kwargs)
        return wrapper   
    return decorated


def cleanup_empty_tasks():
    """Cleans up tasks that are not conneced to a redis job anymore."""
    tasks = Task.query.all()
    deletion_number = 0
    for task in tasks:
        if task.get_rq_job() is None:
            deletion_number += 1
            db.session.delete(task)
    current_app.logger.info(f"Background process deleted {deletion_number} detached tasks")
    db.session.commit()

def cleanup_failed_tasks():
    """Checks whether there are failed tasks and adds this to database.
    This is a rare event since task failure is usually handled during 
    pipeline exception handling. Tasks will only be set as failed
    if there is a low-level problem, e.g. a C-extension wants to
    allocate memory and this fails."""
    # get tasks
    tasks = Task.query.all()
    deletion_number = 0
    for task in tasks:
        if task.get_rq_job() is None:
            # job is not available in rq anymore, is not failed
            continue
        else:
            if task.get_rq_job().get_status() == "failed":
                deletion_number += 1
                # determine whehter collection or dataset was processed
                if task.dataset_id is None:
                    set_collection_failed(task.collection_id, task.intervals_id)
                else:
                    set_dataset_failed(task.dataset_id, task.intervals_id)
                # delete tasks
                db.session.delete(task)
    current_app.logger.info(f"Background process deleted {deletion_number} failed tasks")
    db.session.commit()


def send_keep_alive_message():
    NotificationHandler().send_keep_alive()

