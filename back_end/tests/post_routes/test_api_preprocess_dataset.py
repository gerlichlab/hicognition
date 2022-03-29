"""Module with tests realted to preprocessign datasets."""
import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
from flask.globals import current_app
from hicognition.test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
# import sys
# sys.path.append("./")
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
        # create mock csv
        mock_df = pd.DataFrame({
            "chrom": ["chr1"]*3,
            "start": [1, 2, 3],
            "end": [4,5,6]
        })
        mock_df.to_csv( current_app.config["UPLOAD_DIR"] + "/test.bed", index=False, sep="\t")
        # create datasets
        dataset1 = Dataset(
            id=1,
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="cooler",
            user_id=1,
        )
        dataset2 = Dataset(
            id=2,
            dataset_name="test2",
            file_path="/test/path/2",
            filetype="cooler",
            user_id=1,
        )
        dataset3 = Dataset(
            id=3,
            dataset_name="test3",
            file_path="/test/path/3",
            filetype="bedfile",
            user_id=2,
        )
        dataset4 = Dataset(
            id=4,
            dataset_name="test4",
            file_path=current_app.config["UPLOAD_DIR"] + "/test.bed",
            filetype="bedfile",
            user_id=1,
        )
        dataset5 = Dataset(
            id=5,
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="cooler",
            user_id=2,
            public=True,
        )
        dataset6 = Dataset(
            id=6,
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="bigwig",
            user_id=1,
        )
        dataset7 = Dataset(
            id=7,
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="bigwig",
            user_id=1,
        )
        interval1 = Intervals(id=1, name="interval1", windowsize=100000, dataset_id=4)
        interval2 = Intervals(id=2, name="interval2", windowsize=50000, dataset_id=4)
        interval3 = Intervals(id=3, name="interval3", windowsize=400000, dataset_id=4)
        interval4 = Intervals(id=4, name="interval4", windowsize=1000000, dataset_id=4)
        interval5 = Intervals(id=5, name="interval5", windowsize=2000000, dataset_id=4)
        interval6 = Intervals(id=6, name="interval6", windowsize=10000, dataset_id=4)
        interval7 = Intervals(id=7, name="interval7", windowsize=20000, dataset_id=4)
        self.default_data = [
                dataset1,
                dataset2,
                dataset3,
                dataset4,
                dataset5,
                dataset6,
                dataset7,
                interval1,
                interval2,
                interval3,
                interval4,
                interval5,
                interval6,
                interval7,
            ]
        self.incomplete_data = [
                dataset1,
                dataset2,
                dataset3,
                dataset4,
                dataset5,
                dataset6,
                dataset7,
                interval1,
                interval2,
                interval3,
                interval4,
                interval5
        ]

    @patch("app.models.User.launch_task")
    def test_pipeline_pileup_is_called_correctly(self, mock_launch):
        """Tests whether cooler pipeline to do pileups is called correctly."""
        # add data
        db.session.add_all(self.default_data)
        db.session.commit()
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # define call arguments
        data = {"dataset_ids": "[1]", "region_ids": "[4]", "preprocessing_map": "PREPROCESSING_MAP"}
        # dispatch post request
        response = self.client.post(
            "/api/preprocess/datasets/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        # check whether pipeline has been called with right parameters
        intervals = [1, 2,3, 4, 5]
        for interval_id in intervals:
            interval = Intervals.query.get(interval_id)
            for binsize in current_app.config["PREPROCESSING_MAP"][interval.windowsize]["cooler"]:
                mock_launch.assert_any_call(
                    self.app.queues["long"],
                    "pipeline_pileup",
                    "run pileup pipeline",
                    1,
                    intervals_id=interval.id,
                    binsize=binsize,
                )

    @patch("app.models.User.launch_task")
    def test_pipeline_pileup_is_called_correctly_w_small_preprocessing_map(self, mock_launch):
        """Tests whether cooler pipeline to do pileups is called correctly."""
        # add data
        db.session.add_all(self.default_data)
        db.session.commit()
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # define call arguments
        data = {"dataset_ids": "[1]", "region_ids": "[4]", "preprocessing_map": "PREPROCESSING_MAP_SMALL_WINDOWSIZES"}
        # dispatch post request
        response = self.client.post(
            "/api/preprocess/datasets/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        # check whether pipeline has been called with right parameters
        intervals = [2, 6, 7]
        for interval_id in intervals:
            interval = Intervals.query.get(interval_id)
            for binsize in current_app.config["PREPROCESSING_MAP_SMALL_WINDOWSIZES"][interval.windowsize]["cooler"]:
                mock_launch.assert_any_call(
                    self.app.queues["long"],
                    "pipeline_pileup",
                    "run pileup pipeline",
                    1,
                    intervals_id=interval.id,
                    binsize=binsize,
                )

    @patch("app.models.User.launch_task")
    def test_user_cannot_access_other_datasets(self, mock_launch):
        """Tests whether cooler pipeline to do pileups is called correctly."""
        # add data
        db.session.add_all(self.default_data)
        db.session.commit()
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # construct post data
        data = {"dataset_ids": "[3]", "region_ids": "[4]", "preprocessing_map": "PREPROCESSING_MAP_SMALL_WINDOWSIZES"}
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
        # add data
        db.session.add_all(self.default_data)
        db.session.commit()
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # construct post data
        data = {"dataset_ids": "[100]", "region_ids": "[4]", "preprocessing_map": "PREPROCESSING_MAP_SMALL_WINDOWSIZES"}
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
        # add data
        db.session.add_all(self.default_data)
        db.session.commit()
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # construct post data
        data = {"region_ids": "[4]"}
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
        # add data
        db.session.add_all(self.default_data)
        db.session.commit()
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # construct post data
        # call args
        data = {"dataset_ids": "[5]", "region_ids": "[4]", "preprocessing_map": "PREPROCESSING_MAP"}
        # dispatch post request
        response = self.client.post(
            "/api/preprocess/datasets/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        # check whether pipeline has been called with right parameters
        intervals = [1, 2,3, 4, 5]
        for interval_id in intervals:
            interval = Intervals.query.get(interval_id)
            for binsize in current_app.config["PREPROCESSING_MAP"][interval.windowsize]["cooler"]:
                mock_launch.assert_any_call(
                    self.app.queues["long"],
                    "pipeline_pileup",
                    "run pileup pipeline",
                    5,
                    intervals_id=interval.id,
                    binsize=binsize,
                )

    @patch("app.models.User.launch_task")
    def test_pipeline_stackup_is_called_correctly_for_owned_dataset(self, mock_launch):
        """Tests whether bigwig pipeline to do pileups is called correctly."""
        # add data
        db.session.add_all(self.default_data)
        db.session.commit()
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # construct post data
        data = {"dataset_ids": "[6]", "region_ids": "[4]", "preprocessing_map": "PREPROCESSING_MAP"}
        # dispatch post request
        response = self.client.post(
            "/api/preprocess/datasets/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        # check whether pipeline has been called with right parameters
        intervals = [1, 2,3, 4, 5]
        for interval_id in intervals:
            interval = Intervals.query.get(interval_id)
            for binsize in current_app.config["PREPROCESSING_MAP"][interval.windowsize]["bigwig"]:
                mock_launch.assert_any_call(
                    self.app.queues["medium"],
                    "pipeline_stackup",
                    "run stackup pipeline",
                    6,
                    intervals_id=interval.id,
                    binsize=binsize,
                )

    @patch("app.models.User.launch_task")
    @patch("app.models.Task.get_rq_job")
    def test_failed_tasks_deleted_after_relaunch(self, mock_get_rq_job, mock_launch):
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
        # add tasks to be deleted
        task1 = Task(id="test", name="test", user_id=1, dataset_id=1, intervals_id=1)
        task2 = Task(id="test2", name="test2", user_id=1, dataset_id=1, intervals_id=1)
        # add tasks to be left alone
        task3 = Task(id="test3", name="test2", user_id=1, dataset_id=1, intervals_id=10)
        task4 = Task(id="test4", name="test2", user_id=1, dataset_id=2, intervals_id=1)
        db.session.add_all([task1, task2, task3, task4])
        db.session.commit()
        data = {"dataset_ids": "[1]", "region_ids": "[4]", "preprocessing_map": "PREPROCESSING_MAP"}
        # dispatch post request
        response = self.client.post(
            "/api/preprocess/datasets/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        # check correct tasks where deleted
        self.assertEqual(Task.query.all(), [task3, task4])

    @patch("app.models.User.launch_task")
    def test_mixed_pipelines_called_correctly_with_multiple_owned_datasets(
        self, mock_launch
    ):
        """Tests whether bigwig pipeline to do pileups is called correctly."""
        # add data
        db.session.add_all(self.default_data)
        db.session.commit()
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # construct post data
        data = {"dataset_ids": "[2, 6]", "region_ids": "[4]", "preprocessing_map": "PREPROCESSING_MAP"}
        # dispatch post request
        response = self.client.post(
            "/api/preprocess/datasets/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        # check whether pipeline has been called with right parameters
        intervals = [1]
        datasets = [2, 6]
        for interval_id in intervals:
            interval = Intervals.query.get(interval_id)
            for dataset_id in datasets:
                dataset = Dataset.query.get(dataset_id)
                for binsize in current_app.config["PREPROCESSING_MAP"][interval.windowsize][dataset.filetype]:
                    mock_launch.assert_any_call(
                        current_app.queues[
                            current_app.config["PIPELINE_QUEUES"][
                                dataset.filetype
                            ]
                        ],
                        *current_app.config["PIPELINE_NAMES"][
                            dataset.filetype
                        ],
                        dataset_id,
                        intervals_id=interval.id,
                        binsize=binsize,
                    )
        # check whether processing datasets where added correctly
        region_dataset = Dataset.query.get(4)
        feature_datasets = Dataset.query.filter(Dataset.id.in_([2, 6])).all()
        self.assertEqual(region_dataset.processing_features, feature_datasets)

    @patch("app.models.User.launch_task")
    def test_pipeline_stackup_is_called_correctly_for_multiple_owned_datasets(
        self, mock_launch
    ):
        """Tests whether bigwig pipeline to do pileups is called correctly."""
        # add data
        db.session.add_all(self.default_data)
        db.session.commit()
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # construct post data
        data = {"dataset_ids": "[6, 7]", "region_ids": "[4]", "preprocessing_map": "PREPROCESSING_MAP"}
        # dispatch post request
        response = self.client.post(
            "/api/preprocess/datasets/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        # check whether pipeline has been called with right parameters
        intervals = [1, 2, 4, 5]
        datasets = [6, 7]
        for interval_id in intervals:
            interval = Intervals.query.get(interval_id)
            for dataset_id in datasets:
                dataset = Dataset.query.get(dataset_id)
                for binsize in current_app.config["PREPROCESSING_MAP"][interval.windowsize][dataset.filetype]:
                    mock_launch.assert_any_call(
                        self.app.queues["medium"],
                        "pipeline_stackup",
                        "run stackup pipeline",
                        dataset_id,
                        intervals_id=interval.id,
                        binsize=binsize,
                    )


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
