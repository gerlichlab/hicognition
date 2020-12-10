import os
from test_helpers import LoginTestCase, TempDirTestCase
from unittest.mock import patch

# add path to import app
import sys

sys.path.append("./")
from app import db
from app.models import Dataset, Pileupregion, Pileup


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
        dataset3 = Dataset(id=3, file_path=file_path_3, filetype="bed", user_id=1,)
        # create not owned data_set bed
        file_path_4 = self.create_empty_file_in_tempdir("test2.bed")
        dataset4 = Dataset(id=4, file_path=file_path_4, filetype="cooler", user_id=2,)
        # create pileupregion for owned data_set
        file_path_pr_1 = self.create_empty_file_in_tempdir("test1.bedpe")
        pileup_region_1 = Pileupregion(id=1, dataset_id=3, file_path=file_path_pr_1)
        # create pileupregion for not owned data_set
        file_path_pr_2 = self.create_empty_file_in_tempdir("test2.bedpe")
        pileup_region_2 = Pileupregion(id=2, dataset_id=4, file_path=file_path_pr_2)
        # create pileup for owned data_sets
        file_path_pu_1 = self.create_empty_file_in_tempdir("test1.csv")
        pileup_1 = Pileup(
            id=1, file_path=file_path_pu_1, cooler_id=1, pileupregion_id=1
        )
        # create pileup for not owned data_set
        file_path_pu_2 = self.create_empty_file_in_tempdir("test2.csv")
        pileup_2 = Pileup(
            id=2, file_path=file_path_pu_2, cooler_id=2, pileupregion_id=2
        )
        # add to database
        db.session.add_all(
            [
                dataset1,
                dataset2,
                dataset3,
                dataset4,
                pileup_region_1,
                pileup_region_2,
                pileup_1,
                pileup_2,
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
        self.assertEqual(response.status_code, 401)