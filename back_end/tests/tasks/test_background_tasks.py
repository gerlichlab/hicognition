"""Module with the tests for the background cleanup tasks."""

import unittest
from unittest.mock import MagicMock, patch

# add path to import app
# import sys
# sys.path.append("./")
from app import db
from app.background_tasks import (
    add_app_context,
    cleanup_empty_tasks,
    cleanup_failed_tasks,
)
from app.models import Collection, Dataset, Intervals, Task
from tests.test_utils.test_helpers import LoginTestCase


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
        self.task_w_job2 = Task(id="wJob2")
        self.task_wo_job = Task(id="woJob1")
        self.task_wo_job2 = Task(id="woJob2")
        # The cleanup runs in an app context of its own, whose session loads the tasks anew,
        # so get_rq_job is patched on the class, with the job each task id has
        jobs = {
            "wJob1": "I am a rq-job",
            "wJob2": "I am a rq job",
            "woJob1": None,
            "woJob2": None,
        }
        patcher = patch(
            "app.models.Task.get_rq_job",
            autospec=True,
            side_effect=lambda task: jobs[task.id],
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    @patch("app.background_tasks.current_app.logger")
    def test_deletes_nothing_if_jobs_running(self, mock_log):
        """tests that background-job does not delete anything
        if all tasks are connected to a redis job"""
        db.session.add_all([self.task_w_job, self.task_w_job2])
        db.session.commit()
        # dispatch call
        add_app_context(self.app)(cleanup_empty_tasks)()
        # check whether Tasks are still there
        self.assertEqual(2, len(Task.query.all()))

    @patch("app.background_tasks.current_app.logger")
    def test_deletes_everything_if_only_stopped_jobs(self, mock_log):
        """tests delete everything if only stopped jobs"""
        db.session.add_all([self.task_wo_job, self.task_wo_job2])
        db.session.commit()
        # dispatch call
        add_app_context(self.app)(cleanup_empty_tasks)()
        # check whether Tasks are still there
        self.assertEqual(0, len(Task.query.all()))

    @patch("app.background_tasks.current_app.logger")
    def test_correct_jobs_if_mixture_of_running_and_stopped(self, mock_log):
        """tests that correct jobs are deleted if mixue"""
        db.session.add_all(
            [self.task_w_job, self.task_w_job2, self.task_wo_job, self.task_wo_job2]
        )
        db.session.commit()
        # dispatch call
        add_app_context(self.app)(cleanup_empty_tasks)()
        # check whether Tasks are still there
        self.assertEqual(2, len(Task.query.all()))
        self.assertEqual("wJob1", db.session.get(Task, "wJob1").id)
        self.assertEqual("wJob2", db.session.get(Task, "wJob2").id)


class TestCleanupFailedTasks(LoginTestCase):
    """Tests cleanup of failed tasks"""

    def setUp(self):
        super().setUp()
        # create example tasks
        self.detached_task = Task(
            id="wJob1",
        )
        self.completed_task = Task(id="wJob2")
        self.failed_task_no_associations = Task(id="wJob3")
        self.failed_task_dataset = Task(id="wJob4", dataset_id=2, intervals_id=1)
        self.failed_task_collection = Task(id="wJob4", collection_id=1, intervals_id=1)
        # add datasets, collections and intervals
        self.bed = self.create_dataset(
            id=1, user_id=1, dataset_name="test", filetype="bedfile"
        )
        self.cooler = self.create_dataset(
            id=2, user_id=1, dataset_name="test", filetype="coolerfile"
        )
        self.collection = Collection(
            id=1,
        )
        self.intervals = Intervals(id=1, dataset_id=1)
        # add return objects that signal task status
        completion_sayer = MagicMock()
        completion_sayer.get_status.return_value = "complete"
        failed_sayer = MagicMock()
        failed_sayer.get_status.return_value = "failed"
        # The cleanup runs in an app context of its own, whose session loads the tasks anew,
        # so get_rq_job is patched on the class, with the job each task id has
        jobs = {
            "wJob1": None,
            "wJob2": completion_sayer,
            "wJob3": failed_sayer,
            "wJob4": failed_sayer,
        }
        patcher = patch(
            "app.models.Task.get_rq_job",
            autospec=True,
            side_effect=lambda task: jobs[task.id],
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_good_tasks_not_touched(self):
        """Tests whether tasks that are not failed are not deleted"""
        db.session.add_all([self.detached_task, self.completed_task])
        db.session.commit()
        # dispatch call
        add_app_context(self.app)(cleanup_failed_tasks)()
        # check whether all tasks are still there
        self.assertEqual(2, len(Task.query.all()))

    @patch("app.background_tasks.set_dataset_failed")
    @patch("app.background_tasks.set_collection_failed")
    def test_bad_tasks_removed(
        self, mock_set_collection_failed, mock_set_dataset_failed
    ):
        """Tests whether tasks that failed are deleted"""
        db.session.add_all(
            [self.detached_task, self.completed_task, self.failed_task_no_associations]
        )
        db.session.commit()
        # dispatch call
        add_app_context(self.app)(cleanup_failed_tasks)()
        # check whether all tasks are still there
        self.assertEqual(2, len(Task.query.all()))
        self.assertTrue("wJob3" not in [task.id for task in Task.query.all()])

    @patch("app.pipeline_steps.current_app.logger.error")
    def test_update_failed_dataset(self, mock_error):
        """Tests whether setting a dataset failed works"""
        # add stuff to database
        db.session.add_all(
            [self.failed_task_dataset, self.bed, self.cooler, self.intervals]
        )
        db.session.commit()
        # dispatch call
        add_app_context(self.app)(cleanup_failed_tasks)()
        # check whether task has been removed
        self.assertEqual(0, len(Task.query.all()))
        # check whether dataset has been set failed
        bedfile = db.session.get(Dataset, 1)
        coolerfile = db.session.get(Dataset, 2)
        self.assertEqual(bedfile.failed_features[0], coolerfile)

    @patch("app.pipeline_steps.current_app.logger.error")
    def test_update_failed_collection(self, mock_error):
        """Tests whether setting a collection failed works"""
        # add stuff to database
        db.session.add_all(
            [self.failed_task_collection, self.bed, self.collection, self.intervals]
        )
        db.session.commit()
        # dispatch call
        add_app_context(self.app)(cleanup_failed_tasks)()
        # check whether task has been removed
        self.assertEqual(0, len(Task.query.all()))
        # check whether dataset has been set failed
        bedfile = db.session.get(Dataset, 1)
        collection = db.session.get(Collection, 1)
        self.assertEqual(bedfile.failed_collections[0], collection)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
