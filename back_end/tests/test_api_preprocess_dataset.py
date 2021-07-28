import sys
import unittest
from unittest.mock import MagicMock, patch

from flask.globals import current_app
from test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
sys.path.append("./")
from app import db
from app.models import Dataset, Task, Intervals


class TestPreprocessDataset(LoginTestCase, TempDirTestCase):
    """Tests correct launching of
    pipelines after posting parameters to /preprocess/datasets/ route.
    Inherits both from LoginTest and TempDirTestCase
    to be able to login and make temporary directory"""

    def setUp(self):
        """adds test datasets to db"""
        super().setUp()
        dataset1 = Dataset(
            dataset_name="test1", file_path="/test/path/1", filetype="cooler", user_id=1
        )
        dataset2 = Dataset(
            dataset_name="test2", file_path="/test/path/2", filetype="cooler", user_id=1
        )
        dataset3 = Dataset(
            dataset_name="test3",
            file_path="/test/path/3",
            filetype="bedfile",
            user_id=2,
        )
        dataset4 = Dataset(
            dataset_name="test4", file_path="test/path/4", filetype="bedfile", user_id=1
        )
        dataset5 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="cooler",
            user_id=2,
            public=True,
        )
        dataset6 = Dataset(
            dataset_name="test1", file_path="/test/path/1", filetype="bigwig", user_id=1
        )
        interval1 = Intervals(name="interval1", windowsize=100000, dataset_id=4)
        db.session.add_all(
            [dataset1, dataset2, dataset3, dataset4, dataset5, dataset6, interval1]
        )
        db.session.commit()

    @patch("app.models.User.launch_task")
    def test_pipeline_pileup_is_called_correctly(self, mock_launch):
        """Tests whether cooler pipeline to do pileups is called correctly."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # define call arguments
        data = {
            "dataset_id": "1",
            "region_ids": "[4]",
        }
        # dispatch post request
        response = self.client.post(
            "/api/preprocess/datasets/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        # check whether pipeline has been called with right parameters
        binsizes = current_app.config["PREPROCESSING_MAP"][100000]
        intervals = [1]
        for binsize in binsizes:
            for interval in intervals:
                mock_launch.assert_any_call(
                    "pipeline_pileup",
                    "run pileup pipeline",
                    1,
                    interval,
                    binsize,
                )
        # check whether number of calls was correct
        self.assertEqual(
            len(mock_launch.call_args_list), len(intervals) * len(binsizes)
        )

    @patch("app.models.User.launch_task")
    def test_user_cannot_access_other_datasets(self, mock_launch):
        """Tests whether cooler pipeline to do pileups is called correctly."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # construct post data
        data = {
            "dataset_id": "3",
            "region_ids": "[4]",
        }
        # dispatch post request
        response = self.client.post(
            "/api/preprocess/datasets/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 403)

    @patch("app.models.User.launch_task")
    def test_404_on_non_existent_dataset(self, mock_launch):
        """Tests whether cooler pipeline to do pileups is called correctly."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # construct post data
        data = {
            "dataset_id": "100",
            "region_ids": "[4]",
        }
        # dispatch post request
        response = self.client.post(
            "/api/preprocess/datasets/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 404)

    @patch("app.models.User.launch_task")
    def test_400_on_bad_form(self, mock_launch):
        """Tests whether cooler pipeline to do pileups is called correctly."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # construct post data
        data = {
            "region_ids": "[4]",
        }
        # dispatch post request
        response = self.client.post(
            "/api/preprocess/datasets/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    @patch("app.models.User.launch_task")
    def test_pipeline_pileup_is_called_correctly_for_public_unowned_dataset(
        self, mock_launch
    ):
        """Tests whether cooler pipeline to do pileups is called correctly."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # construct post data
        # call args
        data = {
            "dataset_id": "5",
            "region_ids": "[4]",
        }
        # dispatch post request
        response = self.client.post(
            "/api/preprocess/datasets/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        # check whether pipeline has been called with right parameters
        binsizes = current_app.config["PREPROCESSING_MAP"][100000]
        intervals = [1]
        for binsize in binsizes:
            for interval in intervals:
                mock_launch.assert_any_call(
                    "pipeline_pileup",
                    "run pileup pipeline",
                    5,
                    interval,
                    binsize,
                )
        # check whether number of calls was correct
        self.assertEqual(
            len(mock_launch.call_args_list), len(intervals) * len(binsizes)
        )

    @patch("app.models.User.launch_task")
    def test_pipeline_stackup_is_called_correctly_for_owned_dataset(self, mock_launch):
        """Tests whether bigwig pipeline to do pileups is called correctly."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # construct post data
        data = {
            "dataset_id": "6",
            "region_ids": "[4]",
        }
        # dispatch post request
        response = self.client.post(
            "/api/preprocess/datasets/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        # check whether pipeline has been called with right parameters
        binsizes = current_app.config["PREPROCESSING_MAP"][100000]
        intervals = [1]
        for binsize in binsizes:
            for interval in intervals:
                mock_launch.assert_any_call(
                    "pipeline_stackup",
                    "run stackup pipeline",
                    6,
                    interval,
                    binsize,
                )
        # check whether number of calls was correct
        self.assertEqual(
            len(mock_launch.call_args_list), len(intervals) * len(binsizes)
        )

    @patch("app.models.User.launch_task")
    @patch("app.models.Task.get_rq_job")
    def test_tasks_deleted_after_relaunch(self, mock_get_rq_job, mock_launch):
        """Tests whether preprocessing api call deletes any remaining
        jobs that have failed."""
        # patch
        mock_job = MagicMock()
        mock_job.get_status.return_value = "failed"
        mock_get_rq_job.return_value = mock_job
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # add tasks
        task1 = Task(id="test", name="test", user_id=1, dataset_id=1, complete=False)
        task2 = Task(id="test2", name="test2", user_id=1, dataset_id=1, complete=False)
        db.session.add_all([task1, task2])
        db.session.commit()
        data = {"dataset_id": "1", "region_ids": "[4]"}
        # dispatch post request
        response = self.client.post(
            "/api/preprocess/datasets/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        # check correct tasks where deleted
        self.assertEqual(len(Task.query.all()), 0)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
