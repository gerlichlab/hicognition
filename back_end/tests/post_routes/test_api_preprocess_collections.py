"""Module with tests realted to preprocessign collections."""
import unittest
import pandas as pd
from unittest.mock import patch, MagicMock
from flask.globals import current_app
from hicognition.test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
# import sys
# sys.path.append("./")
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
        # create mock csv
        mock_df = pd.DataFrame(
            {"chrom": ["chr1"] * 3, "start": [1, 2, 3], "end": [4, 5, 6]}
        )
        mock_df.to_csv(
            current_app.config["UPLOAD_DIR"] + "/test.bed", index=False, sep="\t"
        )
        # create datasets
        dataset1 = Dataset(id=1, filetype="bedfile", user_id=1)
        dataset2 = Dataset(id=2, filetype="bedfile", user_id=1)
        dataset3 = Dataset(
            id=3,
            filetype="bedfile",
            user_id=1,
            file_path=current_app.config["UPLOAD_DIR"] + "/test.bed",
            dataset_name="test",
        )
        dataset4 = Dataset(id=4, filetype="bedfile", user_id=2)
        dataset5 = Dataset(id=5, filetype="bigwig", user_id=1)
        dataset6 = Dataset(id=6, filetype="bigwig", user_id=1)
        dataset7 = Dataset(id=7, filetype="cooler", user_id=1)
        dataset8 = Dataset(id=8, filetype="cooler", user_id=1)
        interval1 = Intervals(id=1, name="interval1", windowsize=100000, dataset_id=3)
        interval2 = Intervals(id=2, name="interval2", windowsize=50000, dataset_id=3)
        interval3 = Intervals(id=3, name="interval3", windowsize=400000, dataset_id=3)
        interval4 = Intervals(id=4, name="interval4", windowsize=1000000, dataset_id=3)
        interval5 = Intervals(id=5, name="interval5", windowsize=2000000, dataset_id=3)
        interval6 = Intervals(id=6, name="interval6", windowsize=10000, dataset_id=3)
        interval7 = Intervals(id=7, name="interval7", windowsize=20000, dataset_id=3)
        # create region collections
        collection = Collection(
            datasets=[dataset1, dataset2], user_id=1, id=1, kind="regions"
        )
        collection2 = Collection(datasets=[dataset3], user_id=2, id=2, kind="regions")
        # create feature collections
        collection3 = Collection(
            datasets=[dataset5, dataset6], user_id=1, id=3, kind="1d-features"
        )
        collection4 = Collection(
            datasets=[dataset7, dataset8], user_id=1, id=4, kind="2d-features"
        )
        self.default_data = [
            dataset1,
            dataset2,
            dataset3,
            dataset4,
            dataset5,
            dataset6,
            dataset7,
            dataset8,
            interval1,
            interval2,
            interval3,
            interval4,
            interval5,
            interval6,
            interval7,
            collection,
            collection2,
            collection3,
            collection4,
        ]
        self.incomplete_data = [
            dataset1,
            dataset2,
            dataset3,
            dataset4,
            dataset5,
            dataset6,
            dataset7,
            dataset8,
            interval1,
            interval2,
            interval3,
            interval4,
            interval5,
            collection,
            collection2,
            collection3,
            collection4,
        ]

    @patch("app.models.User.launch_collection_task")
    def test_pipeline_lola_is_called_correctly(self, mock_launch):
        """Tests whether enrichment analysis is called correctly"""
        # add data
        db.session.add_all(self.default_data)
        db.session.commit()
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # define call arguments
        data = {
            "collection_ids": "[1]",
            "region_ids": "[3]",
            "preprocessing_map": "PREPROCESSING_MAP",
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
        intervals = [1, 2, 3, 4, 5]
        for interval_id in intervals:
            interval = Intervals.query.get(interval_id)
            for binsize in current_app.config["PREPROCESSING_MAP"][interval.windowsize][
                "collections"
            ]["regions"]:
                mock_launch.assert_any_call(
                    self.app.queues["long"],
                    "pipeline_lola",
                    "run lola pipeline",
                    1,
                    intervals_id=interval.id,
                    binsize=binsize,
                )

    @patch("app.models.User.launch_collection_task")
    def test_pipeline_lola_is_called_correctly_w_small_preprocessing_map(
        self, mock_launch
    ):
        """Tests whether enrichment analysis is called correctly"""
        # add data
        db.session.add_all(self.default_data)
        db.session.commit()
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # define call arguments
        data = {
            "collection_ids": "[1]",
            "region_ids": "[3]",
            "preprocessing_map": "PREPROCESSING_MAP_SMALL_WINDOWSIZES",
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
        intervals = [2, 6, 7]
        for interval_id in intervals:
            interval = Intervals.query.get(interval_id)
            for binsize in current_app.config["PREPROCESSING_MAP_SMALL_WINDOWSIZES"][
                interval.windowsize
            ]["collections"]["regions"]:
                mock_launch.assert_any_call(
                    self.app.queues["long"],
                    "pipeline_lola",
                    "run lola pipeline",
                    1,
                    intervals_id=interval.id,
                    binsize=binsize,
                )

    @patch("app.models.User.launch_collection_task")
    def test_intervals_created_if_they_dont_exist(self, mock_launch):
        """Check whether preprocess bedfiles is called when intervals do not exist"""
        db.session.add_all(self.incomplete_data)
        db.session.commit()
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # define call arguments
        data = {
            "collection_ids": "[1]",
            "region_ids": "[3]",
            "preprocessing_map": "PREPROCESSING_MAP_SMALL_WINDOWSIZES",
        }
        # dispatch post request
        response = self.client.post(
            "/api/preprocess/collections/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(7, len(Intervals.query.all()))
        windowsizes = [i.windowsize for i in Intervals.query.all()]
        self.assertTrue(10000 in windowsizes)
        self.assertTrue(20000 in windowsizes)

    @patch("app.models.User.launch_collection_task")
    def test_pipeline_1d_embedding_is_called_correctly(self, mock_launch):
        """Tests whether embedding analysis is called correctly"""
        # add data
        db.session.add_all(self.default_data)
        db.session.commit()
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # define call arguments
        data = {
            "collection_ids": "[3]",
            "region_ids": "[3]",
            "preprocessing_map": "PREPROCESSING_MAP",
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
        intervals = [1, 2, 3, 4, 5]
        for interval_id in intervals:
            interval = Intervals.query.get(interval_id)
            for binsize in current_app.config["PREPROCESSING_MAP"][interval.windowsize][
                "collections"
            ]["1d-features"]:
                mock_launch.assert_any_call(
                    self.app.queues["medium"],
                    "pipeline_embedding_1d",
                    "run 1d embedding pipeline",
                    3,
                    intervals_id=interval.id,
                    binsize=binsize,
                )

    @patch("app.models.User.launch_collection_task")
    def test_user_cannot_access_other_collection(self, mock_launch):
        """Tests whether pipeline cannot be started for unowned collection.."""
        # add data
        db.session.add_all(self.default_data)
        db.session.commit()
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # construct post data
        data = {
            "collection_ids": "[2]",
            "region_ids": "[3]",
            "preprocessing_map": "PREPROCESSING_MAP",
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
        # add data
        db.session.add_all(self.default_data)
        db.session.commit()
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # construct post data
        data = {
            "collection_ids": "[100]",
            "region_ids": "[3]",
            "preprocessing_map": "PREPROCESSING_MAP",
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
        # add data
        db.session.add_all(self.default_data)
        db.session.commit()
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # construct post data
        data = {"region_ids": "[3]"}
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
        # add data
        db.session.add_all(self.default_data)
        db.session.commit()
        # patch
        mock_job = MagicMock()
        mock_job.get_status.return_value = "failed"
        mock_get_rq_job.return_value = mock_job
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # add tasks
        task1 = Task(id="test", name="test", user_id=1, collection_id=1, intervals_id=1)
        task2 = Task(
            id="test2", name="test2", user_id=1, collection_id=1, intervals_id=1
        )
        # add tasks that should not be deleted
        task3 = Task(
            id="test3", name="test", user_id=1, collection_id=1, intervals_id=10
        )
        db.session.add_all([task1, task2, task3])
        db.session.commit()
        data = {
            "collection_ids": "[1]",
            "region_ids": "[3]",
            "preprocessing_map": "PREPROCESSING_MAP",
        }
        # dispatch post request
        response = self.client.post(
            "/api/preprocess/collections/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        # check correct tasks where deleted
        self.assertEqual(Task.query.all(), [task3])


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
