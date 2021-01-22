import os
from test_helpers import LoginTestCase, TempDirTestCase
import unittest
from unittest.mock import patch

# add path to import app
import sys

sys.path.append("./")
from app import db
from app.models import Dataset, Intervals, AverageIntervalData


class TestDeleteDatasets(LoginTestCase, TempDirTestCase):
    """ Tests for deletion of datasets."""

    def create_empty_file_in_tempdir(self, file_name):
        file_path = os.path.join(TempDirTestCase.TEMP_PATH, file_name)
        open(file_path, "w").close()
        return file_path

    def add_test_datasets(self):
        """adds test datasets to db"""
        # create owned data_set cooler
        file_path_1 = self.create_empty_file_in_tempdir("test1.mcool")
        dataset1 = Dataset(id=1, file_path=file_path_1, filetype="cooler", user_id=1,)
        # create not owned data_set
        file_path_2 = self.create_empty_file_in_tempdir("test2.mcool")
        dataset2 = Dataset(id=2, file_path=file_path_2, filetype="cooler", user_id=2,)
        # create owned data_set bed
        file_path_3 = self.create_empty_file_in_tempdir("test1.bed")
        dataset3 = Dataset(id=3, file_path=file_path_3, filetype="bedfile", user_id=1,)
        # create not owned data_set bed
        file_path_4 = self.create_empty_file_in_tempdir("test2.bed")
        dataset4 = Dataset(id=4, file_path=file_path_4, filetype="bedfile", user_id=2,)
        # create Intervals for owned data_set
        file_path_pr_1 = self.create_empty_file_in_tempdir("test1.bedpe")
        intervals_1 = Intervals(id=1, dataset_id=3, file_path=file_path_pr_1)
        # create Intervals for not owned data_set
        file_path_pr_2 = self.create_empty_file_in_tempdir("test2.bedpe")
        intervals_2 = Intervals(id=2, dataset_id=4, file_path=file_path_pr_2)
        # create averageIntervalData for owned data_sets
        file_path_pu_1 = self.create_empty_file_in_tempdir("test1.csv")
        averageIntervalData_1 = AverageIntervalData(
            id=1, file_path=file_path_pu_1, cooler_id=1, intervals_id=1
        )
        # create averageIntervalData for not owned data_set
        file_path_pu_2 = self.create_empty_file_in_tempdir("test2.csv")
        averageIntervalData_2 = AverageIntervalData(
            id=2, file_path=file_path_pu_2, cooler_id=2, intervals_id=2
        )
        # add to database
        db.session.add_all(
            [
                dataset1,
                dataset2,
                dataset3,
                dataset4,
                intervals_1,
                intervals_2,
                averageIntervalData_1,
                averageIntervalData_2,
            ]
        )
        db.session.commit()

    def test_no_auth(self):
        """No authentication provided, response should be 401"""
        # protected route
        response = self.client.delete(
            "/api/datasets/1/", content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

    def test_delete_wo_dataset_id(self):
        """Should return 405 since delete is not allowed for /api/datasets"""
        response = self.client.delete("/api/datasets/", content_type="application/json")
        self.assertEqual(response.status_code, 405)

    def test_delete_dataset_does_not_exist(self):
        """test deletion of data set that does not exist."""
        token = self.add_and_authenticate("test", "asdf")
        # create token_headers
        token_headers = self.get_token_header(token)
        # add datasets
        self.add_test_datasets()
        # try deletion of dataset that is not owned, current user is id 1 and dataset id2 is owned
        # by user id 2
        response = self.client.delete(
            "/api/datasets/5/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_dataset_wo_permission(self):
        """Should return 403 since dataset is not owned."""
        token = self.add_and_authenticate("test", "asdf")
        # create token_headers
        token_headers = self.get_token_header(token)
        # add datasets
        self.add_test_datasets()
        # try deletion of dataset that is not owned, current user is id 1 and dataset id2 is owned
        # by user id 2
        response = self.client.delete(
            "/api/datasets/2/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_owned_cooler_dataset(self):
        """test delete owned dataset."""
        token = self.add_and_authenticate("test", "asdf")
        # create token_headers
        token_headers = self.get_token_header(token)
        # add datasets
        self.add_test_datasets()
        # delete data set
        response = self.client.delete(
            "/api/datasets/1/",
            headers=token_headers,
            content_type="application/json",
        )
        # check response
        self.assertEqual(response.status_code, 200)
        # check database state
        dataset_ids = set(entry.id for entry in Dataset.query.all())
        self.assertEqual(dataset_ids, {2, 3, 4})
        intervals_ids = set(entry.id for entry in Intervals.query.all())
        self.assertEqual(intervals_ids, {1, 2})
        averageIntervalData_ids = set(entry.id for entry in AverageIntervalData.query.all())
        self.assertEqual(averageIntervalData_ids, {2})
        # check temp_idr state
        files_tempdir = set(os.listdir(TempDirTestCase.TEMP_PATH))
        expected = {
            "test2.mcool",
            "test1.bed",
            "test2.bed",
            "test1.bedpe",
            "test2.bedpe",
            "test2.csv"
        }
        self.assertEqual(files_tempdir, expected)

    def test_delete_owned_bed_dataset(self):
        """test delete owned dataset."""
        token = self.add_and_authenticate("test", "asdf")
        # create token_headers
        token_headers = self.get_token_header(token)
        # add datasets
        self.add_test_datasets()
        # delete data set
        response = self.client.delete(
            "/api/datasets/3/",
            headers=token_headers,
            content_type="application/json",
        )
        # check response
        self.assertEqual(response.status_code, 200)
        # check database state
        dataset_ids = set(entry.id for entry in Dataset.query.all())
        self.assertEqual(dataset_ids, {1, 2, 4})
        intervals_ids = set(entry.id for entry in Intervals.query.all())
        self.assertEqual(intervals_ids, {2})
        averageIntervalData_ids = set(entry.id for entry in AverageIntervalData.query.all())
        self.assertEqual(averageIntervalData_ids, {2})
        # check temp_idr state
        files_tempdir = set(os.listdir(TempDirTestCase.TEMP_PATH))
        expected = {
            "test1.mcool",
            "test2.mcool",
            "test2.bed",
            "test2.bedpe",
            "test2.csv"
        }
        self.assertEqual(files_tempdir, expected)

    def test_deletion_of_processing_datasets_does_not_work(self):
        """tests whether deletion of datasets that are processing does not work."""
        token = self.add_and_authenticate("test", "asdf")
        # create token_headers
        token_headers = self.get_token_header(token)
        # add dataset that is processing
        file_path_1 = self.create_empty_file_in_tempdir("test1.mcool")
        dataset1 = Dataset(id=1, file_path=file_path_1, filetype="cooler", user_id=1, processing_state="processing")
        db.session.add(dataset1)
        db.session.commit()
        # delete data set
        response = self.client.delete(
            "/api/datasets/1/",
            headers=token_headers,
            content_type="application/json",
        )
        # check response
        self.assertEqual(response.status_code, 403)

    @patch("app.api.delete_routes.current_app.logger.warning")
    def test_deletion_of_non_existent_file_goes_through(self, mock_log):
        """tests whether deletion of datasets that are processing does not work."""
        token = self.add_and_authenticate("test", "asdf")
        # create token_headers
        token_headers = self.get_token_header(token)
        dataset1 = Dataset(id=1, file_path="/code/tmp/bad_file_path", filetype="cooler", user_id=1, processing_state="finished")
        db.session.add(dataset1)
        db.session.commit()
        # delete data set
        response = self.client.delete(
            "/api/datasets/1/",
            headers=token_headers,
            content_type="application/json",
        )
        # check logger has been called
        mock_log.assert_called_with(
            f"Tried removing /code/tmp/bad_file_path, but file does not exist!"
        )
        # check_dataset entry
        datasets = Dataset.query.all()
        self.assertEqual(len(datasets), 0)

    @patch("app.api.delete_routes.current_app.logger.warning")
    def test_deletion_of_entry_without_filename_goes_through(self, mock_log):
        """tests whether deletion of datasets that are processing does not work."""
        token = self.add_and_authenticate("test", "asdf")
        # create token_headers
        token_headers = self.get_token_header(token)
        dataset1 = Dataset(id=1, file_path=None, filetype="cooler", user_id=1, processing_state="finished")
        db.session.add(dataset1)
        db.session.commit()
        # delete data set
        response = self.client.delete(
            "/api/datasets/1/",
            headers=token_headers,
            content_type="application/json",
        )
        # check logger has been called
        mock_log.assert_called_with(
            f"Tried removing <Dataset None>, but there was no filepath!"
        )
        # check_dataset entry
        datasets = Dataset.query.all()
        self.assertEqual(len(datasets), 0)

if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
