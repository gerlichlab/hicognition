import os
import unittest
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
from unittest.mock import patch
from hicognition.test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
import sys

sys.path.append("./")
from app import db
from app.models import Collection, Dataset, Intervals, EmbeddingIntervalData


class TestCreateRegionFrom2DEmbedding(LoginTestCase, TempDirTestCase):
    """Tests creating a new region from a cluster_id associated with
    an embeddingIntervalData entry"""

    def setUp(self):
        super().setUp()
        # add owned collection
        self.owned_feature_dataset = Dataset(id=1, user_id=1, filetype="cooler")
        # add unowned collection
        self.unowned_feature_dataset = Dataset(id=2, user_id=2, filetype="cooler")
        # add owned bedfile
        self.dummy_regions = pd.DataFrame(
            {
                "chrom": ["chr1"] * 6,
                "start": [0, 100, 200, 300, 400, 500],
                "end": [100, 200, 300, 400, 500, 600],
            }
        )
        self.dummy_regions.to_csv(
            os.path.join(TempDirTestCase.TEMP_PATH, "region.csv"),
            sep="\t",
            header=None,
            index=False,
        )
        self.owned_bedfile = Dataset(
            id=3,
            filetype="bedfile",
            user_id=1,
            file_path=os.path.join(TempDirTestCase.TEMP_PATH, "region.csv"),
            assembly=1,
            cellCycleStage="G2",
            perturbation="none",
            valueType="Peak",
            method="ChipSeq",
            sizeType="Point",
            protein="CTCF",
            directionality="+"

        )
        # add unowned bedfile
        self.unowned_bedfile = Dataset(id=4, filetype="bedfile", user_id=2)
        # add intervals for owned bedfile
        self.owned_intervals = Intervals(
            id=1, dataset_id=self.owned_bedfile.id, windowsize=200000
        )
        # add intervals for unowned bedfile
        self.unowned_intervals = Intervals(
            id=2, dataset_id=self.unowned_bedfile.id, windowsize=200000
        )
        # add embeddingIntervalData with unowned dataset
        self.embeddingData_dataset_unowned = EmbeddingIntervalData(
            id=1,
            binsize=10000,
            dataset_id=self.unowned_feature_dataset.id,
            intervals_id=self.owned_intervals.id,
        )
        # add embeddingIntervalData with unowned intervals
        self.embeddingData_intervals_unowned = EmbeddingIntervalData(
            id=2,
            binsize=10000,
            dataset_id=self.owned_feature_dataset.id,
            intervals_id=self.unowned_intervals.id,
        )
        # add owned embeddingIntervalData without thumbnails/feature_id and cluster_did
        self.embeddingData_intervals_wo_thumbnail_data = EmbeddingIntervalData(
            id=4,
            binsize=10000,
            dataset_id=self.owned_feature_dataset.id,
            intervals_id=self.owned_intervals.id,
        )
        # add embeddingIntervalData with owned intervals and collection and associated data
        self.test_data = np.array([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10], [11, 12]])
        data_path = os.path.join(TempDirTestCase.TEMP_PATH, "test.npy")
        np.save(data_path, self.test_data)
        # create thumbnails
        thumbnails = [
            np.array([[5, 6], [7, 7]]),
            np.array([[1, 2], [3, 4]]),
            np.array([[1.5, 10], [7.0, 3.4]]),
        ]
        self.thumbnail_data = np.stack(thumbnails)
        thumbnail_path = os.path.join(TempDirTestCase.TEMP_PATH, "test_thumbnails.npy")
        np.save(thumbnail_path, self.thumbnail_data)
        # create clusters
        self.cluster_data = np.array([1.0, 2.0, 3.0, 1.0, 1.0, 2.0])
        cluster_path = os.path.join(TempDirTestCase.TEMP_PATH, "test_clusters.npy")
        np.save(cluster_path, self.cluster_data)
        # create data
        self.embeddingData_owned = EmbeddingIntervalData(
            id=3,
            binsize=10000,
            file_path=data_path,
            dataset_id=self.owned_feature_dataset.id,
            intervals_id=self.owned_intervals.id,
            thumbnail_path=thumbnail_path,
            cluster_id_path=cluster_path,
        )

    def test_no_auth(self):
        """No authentication provided, response should be 401"""
        # protected route
        response = self.client.post(
            "/api/embeddingIntervalData/1/0/create/", content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 401)

    def test_embeddingIntervalData_does_not_exist(self):
        """Test 404 is returned if embeddingIntervalData does not exist."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # make request
        response = self.client.post(
            "/api/embeddingIntervalData/500/0/create/",
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 404)

    def test_dataset_not_owned(self):
        """dataset underlying embeddingIntervalData is not owned"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        db.session.add_all(
            [
                self.owned_bedfile,
                self.unowned_feature_dataset,
                self.owned_intervals,
                self.embeddingData_dataset_unowned,
            ]
        )
        db.session.commit()
        # make request for forbidden collection
        response = self.client.post(
            f"/api/embeddingIntervalData/{self.embeddingData_dataset_unowned.id}/0/create/",
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 403)

    def test_intervals_not_owned(self):
        """Intervals dataset underlying embeddingIntervalData are not owned"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        db.session.add_all(
            [
                self.owned_feature_dataset,
                self.unowned_bedfile,
                self.unowned_intervals,
                self.embeddingData_intervals_unowned,
            ]
        )
        db.session.commit()
        # make request with forbidden intervall
        response = self.client.post(
            f"/api/embeddingIntervalData/{self.embeddingData_intervals_unowned.id}/0/create/",
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 403)

    def test_form_not_present(self):
        """Test whether 400 is returned when there is not form data sent"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        db.session.add_all(
            [
                self.owned_feature_dataset,
                self.owned_bedfile,
                self.owned_intervals,
                self.embeddingData_intervals_wo_thumbnail_data,
            ]
        )
        db.session.commit()
        # make request with forbidden intervall
        response = self.client.post(
            f"/api/embeddingIntervalData/{self.embeddingData_intervals_wo_thumbnail_data.id}/0/create/",
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    def test_form_invalid(self):
        """Test whether 400 is returned when does not contain correct keys"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        db.session.add_all(
            [
                self.owned_feature_dataset,
                self.owned_bedfile,
                self.owned_intervals,
                self.embeddingData_intervals_wo_thumbnail_data,
            ]
        )
        db.session.commit()
        # construct form
        data = {"datasetName": "asdf"}
        # make request with forbidden intervall
        response = self.client.post(
            f"/api/embeddingIntervalData/{self.embeddingData_intervals_wo_thumbnail_data.id}/0/create/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    def test_clusterIDs_do_not_exist(self):
        """Test whether 404 is returned if clusterID field is None"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        db.session.add_all(
            [
                self.owned_feature_dataset,
                self.owned_bedfile,
                self.owned_intervals,
                self.embeddingData_intervals_wo_thumbnail_data,
            ]
        )
        db.session.commit()
        # construct form
        data = {"name": "asdf"}
        # make request with forbidden intervall
        response = self.client.post(
            f"/api/embeddingIntervalData/{self.embeddingData_intervals_wo_thumbnail_data.id}/0/create/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 404)

    @patch("app.models.User.launch_task")
    def test_new_region_correctly_created(self, mock_launch):
        """Test whether new region is correctly created"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        db.session.add_all(
            [
                self.owned_feature_dataset,
                self.owned_bedfile,
                self.owned_intervals,
                self.embeddingData_owned,
            ]
        )
        db.session.commit()
        # construct form
        data = {"name": "asdf"}
        # make request with owned interval
        response = self.client.post(
            f"/api/embeddingIntervalData/{self.embeddingData_owned.id}/1/create/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        # test whether region was created successfully
        self.assertEqual(len(Dataset.query.all()), 3)
        new_dataset = Dataset.query.all()[2]
        self.assertEqual(new_dataset.dataset_name, "asdf")
        self.assertEqual(new_dataset.filetype, "bedfile")
        self.assertEqual(new_dataset.assembly, 1)
        self.assertEqual(new_dataset.cellCycleStage, "G2")
        self.assertEqual(new_dataset.perturbation, "none")
        self.assertEqual(new_dataset.valueType, "Peak")
        self.assertEqual(new_dataset.method, "ChipSeq")
        self.assertEqual(new_dataset.sizeType, "Point")
        self.assertEqual(new_dataset.protein, "CTCF")
        self.assertEqual(new_dataset.directionality, "+")
        # test whether subset is correct
        created_subset = pd.read_csv(new_dataset.file_path, sep="\t", header=None)
        expected_subset = self.dummy_regions.iloc[[0, 3, 4], :].reset_index(drop=True)
        expected_subset.columns = [0, 1 ,2]
        assert_frame_equal(created_subset, expected_subset)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
