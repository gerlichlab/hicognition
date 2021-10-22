import unittest
from unittest.mock import patch
from test_helpers import LoginTestCase


# add path to import app
import sys

sys.path.append("./")
from app import db
from app.models import Task
from app.background_tasks import add_app_context, cleanup_empty_tasks

class TestEmptyJobDeletion(LoginTestCase):
    """tests background task that deletes
    Redis-tasks from the db that are not connected
    to a redis job anymore."""

    def setUp(self):
        super().setUp()
        # create example tasks
        self.task_w_job = Task(
            id="wJob1",
        )
        self.task_w_job2 = Task(
            id="wJob2"
        )
        self.task_wo_job = Task(
            id="woJob1"
        )
        self.task_wo_job2 = Task(
            id="woJob2"
        )
        # monkey patch get_rq_job
        self.task_w_job.get_rq_job = lambda: "I am a rq-job"
        self.task_w_job2.get_rq_job = lambda: "I am a rq job"

    @patch("app.background_tasks.current_app.logger")
    def test_deletes_nothing_if_jobs_running(self, mock_log):
        """tests that background-job does not delete anything
        if all tasks are connected to a redis job"""
        db.session.add_all([self.task_w_job, self.task_w_job2])
        db.session.commit()
        # dispatch call
        add_app_context(self.app)(cleanup_empty_tasks)()
        # check whether Tasks are still there
        self.assertEqual(2,len(Task.query.all()))


    @patch("app.background_tasks.current_app.logger")
    def test_deletes_everything_if_only_stopped_jobs(self, mock_log):
        """tests delete everything if only stopped jobs"""
        db.session.add_all([self.task_wo_job, self.task_wo_job2])
        db.session.commit()
        # dispatch call
        add_app_context(self.app)(cleanup_empty_tasks)()
        # check whether Tasks are still there
        self.assertEqual(0,len(Task.query.all()))

    @patch("app.background_tasks.current_app.logger")
    def test_correct_jobs_if_mixture_of_running_and_stopped(self, mock_log):
        """tests that correct jobs are deleted if mixue"""
        db.session.add_all([self.task_w_job, self.task_w_job2, self.task_wo_job, self.task_wo_job2])
        db.session.commit()
        # dispatch call
        add_app_context(self.app)(cleanup_empty_tasks)()
        # check whether Tasks are still there
        self.assertEqual(2,len(Task.query.all()))
        self.assertEqual("wJob1", Task.query.get("wJob1").id)
        self.assertEqual("wJob2",Task.query.get("wJob2").id)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
