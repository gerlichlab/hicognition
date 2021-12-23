import os
from pathlib import Path
from hicognition.test_helpers import LoginTestCase, TempDirTestCase
import unittest
from unittest.mock import patch

# add path to import app
import sys

sys.path.append("./")
from app import db
from app.models import (
    Dataset,
    Intervals,
    AverageIntervalData,
    IndividualIntervalData,
    Session,
    Collection,
)


class TestDeleteDatasets(LoginTestCase, TempDirTestCase):
    """ Tests for deletion of datasets."""

    def _create_empty_file_in_tempdir(self, file_name):
        file_path = os.path.join(self.TEMP_PATH, file_name)
        open(file_path, "w").close()
        return file_path

    def _create_files_for_datasets(self, datasets):
        """creates empty files for datasets"""
        file_number = 0
        for dataset in datasets:
            temp_file = self._create_empty_file_in_tempdir(f"test_{file_number}")
            dataset.file_path = temp_file
            if isinstance(dataset, IndividualIntervalData):
                temp_file_2 = self._create_empty_file_in_tempdir(
                    f"test_small_{file_number}"
                )
                dataset.file_path_small = temp_file_2
            file_number += 1
        db.session.commit()

    def _get_expected_tempdir_state(self, datasets, deletion_id):
        expected_files = []
        for dataset in datasets:
            if dataset.id != deletion_id:
                expected_files.append(Path(dataset.file_path).name)
                # get intervals
                for interval in dataset.intervals:
                    expected_files.append(Path(interval.file_path).name)
                # get average interval data
                for avg_data in dataset.averageIntervalData:
                    expected_files.append(Path(avg_data.file_path).name)
                for ind_data in dataset.individualIntervalData:
                    expected_files.append(Path(ind_data.file_path).name)
                    expected_files.append(Path(ind_data.file_path_small).name)
        return expected_files

    def setUp(self):
        """adds test datasets to db"""
        super().setUp()
        # create owned data_set cooler
        self.owned_cooler = Dataset(id=1, filetype="cooler", user_id=1)
        # create not owned data_set
        self.unowned_cooler = Dataset(id=2, filetype="cooler", user_id=2)
        # create owned data_set bed
        self.owned_bedfile = Dataset(id=3, filetype="bedfile", user_id=1)
        # create not owned data_set bed
        self.unowned_bedfile = Dataset(id=4, filetype="bedfile", user_id=2)
        # create owned data_set bigwig
        self.owned_bigwig = Dataset(id=5, filetype="bigwig", user_id=1)
        # create cooler that is in processing state
        self.owned_cooler_w_wrong_path = Dataset(
            id=7, filetype="cooler", file_path="/code/tmp/bad_file_path", user_id=1
        )
        # create public, unowned cooler
        self.unowned_public_cooler = Dataset(
            id=8, filetype="cooler", user_id=2, public=True
        )
        # create public, owned cooler
        self.owned_public_cooler = Dataset(
            id=9, filetype="cooler", user_id=1, public=True
        )
        # create Intervals for owned data_set
        self.owned_intervals = Intervals(id=1, dataset_id=3)
        # create Intervals for not owned data_set
        self.unowned_intervals = Intervals(id=2, dataset_id=4)
        # create averageIntervalData for owned data_set cooler
        self.average_interval_cooler_owned = AverageIntervalData(
            id=1, dataset_id=1, intervals_id=1
        )
        # create averageIntervalData for not owned data_set
        self.average_interval_cooler_unowned = AverageIntervalData(
            id=2, dataset_id=2, intervals_id=2
        )
        # create averageIntervalData for owned data_set bigwig
        self.average_interval_bigwig_owned = AverageIntervalData(
            id=3, dataset_id=5, intervals_id=1
        )
        # create individualIntervalData for owned data_sets
        self.individual_interval_bigwig_owned = IndividualIntervalData(
            id=1, dataset_id=5, intervals_id=1
        )
        # create sessions
        self.session_owned_cooler = Session(datasets=[self.owned_cooler])
        self.session_unowned_cooler = Session(datasets=[self.unowned_cooler])
        # create collection
        self.owned_collection = Collection(datasets=[self.owned_cooler])
        # groupings
        self.datasets = [
            self.owned_cooler,
            self.unowned_cooler,
            self.owned_bedfile,
            self.unowned_bedfile,
            self.owned_bigwig,
        ]
        self.intervals = [self.owned_intervals, self.unowned_intervals]
        self.average_interval_data = [
            self.average_interval_bigwig_owned,
            self.average_interval_cooler_owned,
            self.average_interval_cooler_unowned,
        ]
        self.individual_interval_data = [self.individual_interval_bigwig_owned]
        self.all_data = (
            self.datasets
            + self.intervals
            + self.individual_interval_data
            + self.average_interval_data
        )

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
        # try deletion of dataset that is not owned, current user is id 1 and dataset id2 is owned
        # by user id 2
        response = self.client.delete(
            "/api/datasets/500/", headers=token_headers, content_type="application/json"
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_dataset_wo_permission(self):
        """Should return 403 since dataset is not owned."""
        token = self.add_and_authenticate("test", "asdf")
        # create token_headers
        token_headers = self.get_token_header(token)
        # add dataset
        db.session.add(self.unowned_cooler)
        db.session.commit()
        # dispatch response
        response = self.client.delete(
            "/api/datasets/2/", headers=token_headers, content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_owned_cooler_dataset(self):
        """test delete owned dataset."""
        token = self.add_and_authenticate("test", "asdf")
        # create token_headers
        token_headers = self.get_token_header(token)
        # add datasets
        db.session.add_all(self.all_data)
        db.session.commit()
        self._create_files_for_datasets(self.all_data)
        # delete data set
        deletion_id = 1
        response = self.client.delete(
            f"/api/datasets/{deletion_id}/",
            headers=token_headers,
            content_type="application/json",
        )
        # check response
        self.assertEqual(response.status_code, 200)
        # check database state
        dataset_ids = set(entry.id for entry in Dataset.query.all())
        self.assertEqual(dataset_ids, {2, 3, 4, 5})
        intervals_ids = set(entry.id for entry in Intervals.query.all())
        self.assertEqual(intervals_ids, {1, 2})
        averageIntervalData_ids = set(
            entry.id for entry in AverageIntervalData.query.all()
        )
        self.assertEqual(averageIntervalData_ids, {2, 3})
        individualIntervalData_ids = set(
            entry.id for entry in IndividualIntervalData.query.all()
        )
        self.assertEqual(individualIntervalData_ids, {1})
        # check temp_dir state
        files_tempdir = set(os.listdir(TempDirTestCase.TEMP_PATH))
        expected = set(self._get_expected_tempdir_state(self.datasets, deletion_id))
        self.assertEqual(files_tempdir, expected)

    def test_delete_owned_bed_dataset(self):
        """test delete owned dataset."""
        token = self.add_and_authenticate("test", "asdf")
        # create token_headers
        token_headers = self.get_token_header(token)
        # add datasets
        db.session.add_all(self.all_data)
        db.session.commit()
        self._create_files_for_datasets(self.all_data)
        # delete data set
        deletion_id = 3
        response = self.client.delete(
            f"/api/datasets/{deletion_id}/",
            headers=token_headers,
            content_type="application/json",
        )
        # check response
        self.assertEqual(response.status_code, 200)
        # check database state
        dataset_ids = set(entry.id for entry in Dataset.query.all())
        self.assertEqual(dataset_ids, {1, 2, 4, 5})
        intervals_ids = set(entry.id for entry in Intervals.query.all())
        self.assertEqual(intervals_ids, {2})
        averageIntervalData_ids = set(
            entry.id for entry in AverageIntervalData.query.all()
        )
        self.assertEqual(averageIntervalData_ids, {2})
        individualIntervalData_ids = set(
            entry.id for entry in IndividualIntervalData.query.all()
        )
        self.assertEqual(individualIntervalData_ids, set())
        # check temp_idr state
        files_tempdir = set(os.listdir(TempDirTestCase.TEMP_PATH))
        expected = set(self._get_expected_tempdir_state(self.datasets, deletion_id))
        self.assertEqual(files_tempdir, expected)

    def test_delete_owned_bigwig_dataset(self):
        """test delete owned dataset."""
        token = self.add_and_authenticate("test", "asdf")
        # create token_headers
        token_headers = self.get_token_header(token)
        # add datasets
        db.session.add_all(self.all_data)
        db.session.commit()
        self._create_files_for_datasets(self.all_data)
        # delete data set
        deletion_id = 5
        response = self.client.delete(
            f"/api/datasets/{deletion_id}/",
            headers=token_headers,
            content_type="application/json",
        )
        # check response
        self.assertEqual(response.status_code, 200)
        # check database state
        dataset_ids = set(entry.id for entry in Dataset.query.all())
        self.assertEqual(dataset_ids, {1, 2, 3, 4})
        intervals_ids = set(entry.id for entry in Intervals.query.all())
        self.assertEqual(intervals_ids, {1, 2})
        averageIntervalData_ids = set(
            entry.id for entry in AverageIntervalData.query.all()
        )
        self.assertEqual(averageIntervalData_ids, {1, 2})
        individualIntervalData_ids = set(
            entry.id for entry in IndividualIntervalData.query.all()
        )
        self.assertEqual(individualIntervalData_ids, set())
        # check temp_idr state
        files_tempdir = set(os.listdir(TempDirTestCase.TEMP_PATH))
        expected = set(self._get_expected_tempdir_state(self.datasets, deletion_id))
        self.assertEqual(files_tempdir, expected)

    def test_deletion_of_processing_features_does_not_work(self):
        """tests whether deletion of datasets that are processing does not work."""
        token = self.add_and_authenticate("test", "asdf")
        # create token_headers
        token_headers = self.get_token_header(token)
        # create processing dataset
        owned_cooler_processing = Dataset(
            id=6, filetype="cooler", user_id=1, processing_regions=[self.owned_bedfile]
        )
        # add dataset that is processing
        db.session.add_all([owned_cooler_processing, self.owned_bedfile])
        db.session.commit()
        # delete data set
        response = self.client.delete(
            f"/api/datasets/{owned_cooler_processing.id}/",
            headers=token_headers,
            content_type="application/json",
        )
        # check response
        self.assertEqual(response.status_code, 400)

    def test_deletion_of_processing_regions_does_not_work(self):
        """tests whether deletion of datasets that are processing does not work."""
        token = self.add_and_authenticate("test", "asdf")
        # create token_headers
        token_headers = self.get_token_header(token)
        # create processing dataset
        owned_bedfile_processing = Dataset(
            id=6, filetype="bedfile", user_id=1, processing_features=[self.owned_cooler]
        )
        # add dataset that is processing
        db.session.add_all([owned_bedfile_processing, self.owned_cooler])
        db.session.commit()
        # delete data set
        response = self.client.delete(
            f"/api/datasets/{owned_bedfile_processing.id}/",
            headers=token_headers,
            content_type="application/json",
        )
        # check response
        self.assertEqual(response.status_code, 400)

    def test_deletion_of_non_existent_file_goes_through(self):
        """tests whether deletion of datasets that are processing does not work."""
        token = self.add_and_authenticate("test", "asdf")
        # create token_headers
        token_headers = self.get_token_header(token)
        db.session.add(self.owned_cooler_w_wrong_path)
        db.session.commit()
        # delete data set
        self.client.delete(
            f"/api/datasets/{self.owned_cooler_w_wrong_path.id}/",
            headers=token_headers,
            content_type="application/json",
        )
        # check_dataset entry
        datasets = Dataset.query.all()
        self.assertEqual(len(datasets), 0)

    def test_deletion_of_entry_without_filename_goes_through(self):
        """tests whether deletion of datasets that are processing does not work."""
        token = self.add_and_authenticate("test", "asdf")
        # create token_headers
        token_headers = self.get_token_header(token)
        db.session.add(self.owned_cooler)
        db.session.commit()
        # delete data set
        self.client.delete(
            f"/api/datasets/{self.owned_cooler.id}/",
            headers=token_headers,
            content_type="application/json",
        )
        # check_dataset entry
        datasets = Dataset.query.all()
        self.assertEqual(len(datasets), 0)

    def test_user_cannot_delete_public_but_unowned_dataset(self):
        """Deletion of public dataset does not work."""
        token = self.add_and_authenticate("test", "asdf")
        # create token_headers
        token_headers = self.get_token_header(token)
        db.session.add(self.unowned_public_cooler)
        db.session.commit()
        # delete data set
        response = self.client.delete(
            f"/api/datasets/{self.unowned_public_cooler.id}/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_user_can_delete_public_but_owned_dataset(self):
        """Deletion of public dataset does not work."""
        token = self.add_and_authenticate("test", "asdf")
        # create token_headers
        token_headers = self.get_token_header(token)
        db.session.add(self.owned_public_cooler)
        db.session.commit()
        # delete data set
        response = self.client.delete(
            f"/api/datasets/{self.owned_public_cooler.id}/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def test_deletion_of_dataset_deletes_associated_sessions(self):
        """tests whether deletion of dataset with associated sessions
        causes deletion of these sessions."""
        token = self.add_and_authenticate("test", "asdf")
        # create token_headers
        token_headers = self.get_token_header(token)
        db.session.add_all(
            [
                self.owned_cooler,
                self.unowned_cooler,
                self.session_owned_cooler,
                self.session_unowned_cooler,
            ]
        )
        db.session.commit()
        # delete data set
        self.client.delete(
            f"/api/datasets/{self.owned_cooler.id}/",
            headers=token_headers,
            content_type="application/json",
        )
        # check_dataset entry
        datasets = Dataset.query.all()
        self.assertEqual(len(datasets), 1)
        self.assertEqual(Dataset.query.first(), self.unowned_cooler)
        self.assertEqual(len(Session.query.all()), 1)
        self.assertEqual(Session.query.first(), self.session_unowned_cooler)

    def test_deletion_of_dataset_causes_deletion_of_collection(self):
        """Test whether deletion of dataset causes deletion of containing collection"""
        token = self.add_and_authenticate("test", "asdf")
        # create token_headers
        token_headers = self.get_token_header(token)
        db.session.add_all([self.owned_cooler, self.owned_collection])
        db.session.commit()
        # delete data set
        self.client.delete(
            f"/api/datasets/{self.owned_cooler.id}/",
            headers=token_headers,
            content_type="application/json",
        )
        # check whether collection was deleted
        self.assertEqual(len(Collection.query.all()), 0)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
