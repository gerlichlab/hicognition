import sys
import unittest
from unittest.mock import patch, MagicMock

from flask.globals import current_app
from test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
sys.path.append("./")
from app import db
from app.models import Dataset, Collection, Intervals, Task


class TestPreprocessCollections(LoginTestCase, TempDirTestCase):
    """Tests correct launching of
    pipelines after posting parameters to /preprocess/collections/ route.
    Inherits both from LoginTest and TempDirTestCase
    to be able to login and make temporary directory"""

    def setUp(self):
        """adds test datasets to db"""
        super().setUp()
        # create datasets
        dataset1 = Dataset(id=1, filetype="bedfile", user_id=1)
        dataset2 = Dataset(id=2, filetype="bedfile", user_id=1)
        dataset3 = Dataset(id=3, filetype="bedfile", user_id=1)
        dataset4 = Dataset(id=4, filetype="bedfile", user_id=2)
        dataset5 = Dataset(id=5, filetype="bigwig", user_id=1)
        dataset6 = Dataset(id=6, filetype="bigwig", user_id=1)
        interval1 = Intervals(id=1, name="interval1", windowsize=100000, dataset_id=3)
        # create region collections
        collection = Collection(datasets=[dataset1, dataset2], user_id=1, id=1, kind="region")
        collection2 = Collection(datasets=[dataset3], user_id=2, id=2, kind="region")
        # create feature collections
        collection3 = Collection(datasets=[dataset5, dataset6], user_id=1, id=3, kind="1d-feature")
        db.session.add_all(
            [dataset1, dataset2, dataset3, dataset4, dataset5, dataset6, interval1, collection, collection2, collection3]
        )
        db.session.commit()

    @patch("app.models.User.launch_collection_task")
    def test_pipeline_lola_is_called_correctly(self, mock_launch):
        """Tests whether enrichment analysis is called correctly"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # define call arguments
        data = {
            "collection_id": "1",
            "region_ids": "[3]",
        }
        # dispatch post request
        response = self.client.post(
            "/api/preprocess/collections/",
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
                    "pipeline_lola",
                    "run lola pipeline",
                    1,
                    intervals_id=interval,
                    binsize=binsize,
                )
        # check whether number of calls was correct
        self.assertEqual(
            len(mock_launch.call_args_list), len(intervals) * len(binsizes)
        )



    @patch("app.models.User.launch_collection_task")
    def test_pipeline_1d_embedding_is_called_correctly(self, mock_launch):
        """Tests whether embedding analysis is called correctly"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # define call arguments
        data = {
            "collection_id": "3",
            "region_ids": "[3]",
        }
        # dispatch post request
        response = self.client.post(
            "/api/preprocess/collections/",
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
                    "pipeline_1d_embedding",
                    "run 1d embedding pipeline",
                    3,
                    intervals_id=interval,
                    binsize=binsize,
                )
        # check whether number of calls was correct
        self.assertEqual(
            len(mock_launch.call_args_list), len(intervals) * len(binsizes)
        )

    @patch("app.models.User.launch_collection_task")
    def test_user_cannot_access_other_collection(self, mock_launch):
        """Tests whether pipeline cannot be started for unowned collection.."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # construct post data
        data = {
            "collection_id": "2",
            "region_ids": "[3]",
        }
        # dispatch post request
        response = self.client.post(
            "/api/preprocess/collections/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 403)

    @patch("app.models.User.launch_collection_task")
    def test_404_on_non_existent_collection(self, mock_launch):
        """Tests whether cooler pipeline to do pileups is called correctly."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # construct post data
        data = {
            "collection_id": "100",
            "region_ids": "[3]",
        }
        # dispatch post request
        response = self.client.post(
            "/api/preprocess/collections/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 404)

    @patch("app.models.User.launch_collection_task")
    def test_400_on_bad_form(self, mock_launch):
        """Tests whether bad form raises 400 error."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # construct post data
        data = {
            "region_ids": "[3]",
        }
        # dispatch post request
        response = self.client.post(
            "/api/preprocess/collections/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    @patch("app.models.User.launch_collection_task")
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
        task1 = Task(id="test", name="test", user_id=1, collection_id=1, complete=False)
        task2 = Task(
            id="test2", name="test2", user_id=1, collection_id=1, complete=False
        )
        db.session.add_all([task1, task2])
        db.session.commit()
        data = {"collection_id": "1", "region_ids": "[3]"}
        # dispatch post request
        response = self.client.post(
            "/api/preprocess/collections/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        # check correct tasks where deleted
        self.assertEqual(len(Task.query.all()), 0)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
