"""Module with tests realted to creating new regions from local neighborhoods in embeddings."""
import os
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
from tests.test_utils.test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
# import sys
# sys.path.append("./")
from app import db
from app.models import Collection, Dataset, Intervals, EmbeddingIntervalData


class TestCreateRegionFrom2DEmbedding(LoginTestCase, TempDirTestCase):
    """Tests creating a new region from a cluster_id associated with
    an embeddingIntervalData entry"""

    def setUp(self):
        super().setUp()
        # add owned collection
        self.owned_feature_dataset = self.create_dataset(id=1, dataset_name="test", user_id=1, filetype="cooler")
        # add unowned collection
        self.unowned_feature_dataset = self.create_dataset(id=2, dataset_name="test", user_id=2, filetype="cooler")
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
        self.owned_bedfile = self.create_dataset(
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
            directionality="+",
        )
        # add unowned bedfile
        self.unowned_bedfile = self.create_dataset(id=4, dataset_name="test", filetype="bedfile", user_id=2)
        # add intervals for owned bedfile
        self.owned_intervals = Intervals(
            id=1, dataset_id=self.owned_bedfile.id, windowsize=200000
        )
        # add intervals for unowned bedfile
        self.unowned_intervals = Intervals(
            id=2, dataset_id=self.unowned_bedfile.id, windowsize=200000
        )
        # add embeddingIntervalData with unowned dataset
        self.embedding_data_dataset_unowned = EmbeddingIntervalData(
            id=1,
            binsize=10000,
            dataset_id=self.unowned_feature_dataset.id,
            intervals_id=self.owned_intervals.id,
        )
        # add embeddingIntervalData with unowned intervals
        self.embedding_data_intervals_unowned = EmbeddingIntervalData(
            id=2,
            binsize=10000,
            dataset_id=self.owned_feature_dataset.id,
            intervals_id=self.unowned_intervals.id,
        )
        # add owned embeddingIntervalData without thumbnails/feature_id and cluster_did
        self.embedding_data_intervals_wo_thumbnail_data = EmbeddingIntervalData(
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
        self.embedding_data_owned = EmbeddingIntervalData(
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
            "/api/embeddingIntervalData/1/createRegion/", content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 401)

    def test_embedding_interval_data_does_not_exist(self):
        """Test 404 is returned if embeddingIntervalData does not exist."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # make request
        response = self.client.post(
            "/api/embeddingIntervalData/500/createRegion/",
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
                self.embedding_data_dataset_unowned,
            ]
        )
        db.session.commit()
        # make request for forbidden collection
        response = self.client.post(
            f"/api/embeddingIntervalData/{self.embedding_data_dataset_unowned.id}/createRegion/",
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
                self.embedding_data_intervals_unowned,
            ]
        )
        db.session.commit()
        # make request with forbidden intervall
        response = self.client.post(
            f"/api/embeddingIntervalData/{self.embedding_data_intervals_unowned.id}/createRegion/",
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
                self.embedding_data_intervals_wo_thumbnail_data,
            ]
        )
        db.session.commit()
        # make request with forbidden intervall
        response = self.client.post(
            f"/api/embeddingIntervalData/{self.embedding_data_intervals_wo_thumbnail_data.id}/createRegion/",
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
                self.embedding_data_intervals_wo_thumbnail_data,
            ]
        )
        db.session.commit()
        # construct form
        data = {"datasetName": "asdf"}
        # make request with forbidden intervall
        response = self.client.post(
            f"/api/embeddingIntervalData/{self.embedding_data_intervals_wo_thumbnail_data.id}/createRegion/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    def test_cluster_ids_do_not_exist(self):
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
                self.embedding_data_intervals_wo_thumbnail_data,
            ]
        )
        db.session.commit()
        # construct form
        data = {"name": "asdf", 'cluster_ids': '[0]'}
        # make request with forbidden intervall
        response = self.client.post(
            f"/api/embeddingIntervalData/{self.embedding_data_intervals_wo_thumbnail_data.id}/createRegion/",
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
                self.embedding_data_owned,
            ]
        )
        db.session.commit()
        # construct form
        data = {"name": "asdf", "cluster_ids": "[1]"}
        # make request with owned interval
        response = self.client.post(
            f"/api/embeddingIntervalData/{self.embedding_data_owned.id}/createRegion/",
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
        self.assertEqual(new_dataset.perturbation, "none")
        self.assertEqual(new_dataset.sizeType, "Point")
        # test whether subset is correct
        created_subset = pd.read_csv(new_dataset.file_path, sep="\t", header=None)
        expected_subset = self.dummy_regions.iloc[[0, 3, 4], :].reset_index(drop=True)
        expected_subset.columns = [0, 1, 2]
        assert_frame_equal(created_subset, expected_subset)


class TestCreateRegionFrom1DEmbedding(LoginTestCase, TempDirTestCase):
    """Tests creating a new region from a cluster_id associated with
    an embeddingIntervalData entry when its a 1d-embedding"""

    def setUp(self):
        super().setUp()
        # add owned collection
        self.owned_feature_collection = Collection(id=1, user_id=1, kind="1d-features")
        # add unowned collection
        self.unowned_feature_collection = Collection(
            id=2, user_id=2, kind="1d-features"
        )
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
        self.owned_bedfile = self.create_dataset(
            id=3,
            filetype="bedfile", 
            dataset_name="test",
            user_id=1,
            file_path=os.path.join(TempDirTestCase.TEMP_PATH, "region.csv"),
            assembly=1,
            cellCycleStage="G2",
            perturbation="none",
            valueType="Peak",
            method="ChipSeq",
            sizeType="Point",
            protein="CTCF",
            directionality="+",
        )
        # add unowned bedfile
        self.unowned_bedfile = self.create_dataset(id=4, dataset_name="test", filetype="bedfile", user_id=2)
        # add intervals for owned bedfile
        self.owned_intervals = Intervals(
            id=1, dataset_id=self.owned_bedfile.id, windowsize=200000
        )
        # add intervals for unowned bedfile
        self.unowned_intervals = Intervals(
            id=2, dataset_id=self.unowned_bedfile.id, windowsize=200000
        )
        # add embeddingIntervalData with unowned dataset
        self.embedding_data_collection_unowned = EmbeddingIntervalData(
            id=1,
            binsize=10000,
            value_type="1d-embedding",
            collection_id=self.unowned_feature_collection.id,
            intervals_id=self.owned_intervals.id,
        )
        # add embeddingIntervalData with unowned intervals
        self.embedding_data_intervals_unowned = EmbeddingIntervalData(
            id=2,
            binsize=10000,
            value_type="1d-embedding",
            collection_id=self.owned_feature_collection.id,
            intervals_id=self.unowned_intervals.id,
        )
        # add owned embeddingIntervalData without thumbnails/feature_id and cluster_did
        self.embedding_data_intervals_wo_thumbnail_data = EmbeddingIntervalData(
            id=4,
            binsize=10000,
            value_type="1d-embedding",
            collection_id=self.owned_feature_collection.id,
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
        self.embedding_data_owned = EmbeddingIntervalData(
            id=3,
            binsize=10000,
            file_path=data_path,
            value_type="1d-embedding",
            collection_id=self.owned_feature_collection.id,
            intervals_id=self.owned_intervals.id,
            thumbnail_path=thumbnail_path,
            cluster_id_path=cluster_path,
        )

    def test_embedding_interval_data_does_not_exist(self):
        """Test 404 is returned if embeddingIntervalData does not exist."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # make request
        response = self.client.post(
            "/api/embeddingIntervalData/500/createRegion/",
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 404)

    def test_collection_not_owned(self):
        """collection underlying embeddingIntervalData is not owned"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        db.session.add_all(
            [
                self.owned_bedfile,
                self.unowned_feature_collection,
                self.owned_intervals,
                self.embedding_data_collection_unowned,
            ]
        )
        db.session.commit()
        # make request for forbidden collection
        response = self.client.post(
            f"/api/embeddingIntervalData/{self.embedding_data_collection_unowned.id}/createRegion/",
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
                self.owned_feature_collection,
                self.unowned_bedfile,
                self.unowned_intervals,
                self.embedding_data_intervals_unowned,
            ]
        )
        db.session.commit()
        # make request with forbidden intervall
        response = self.client.post(
            f"/api/embeddingIntervalData/{self.embedding_data_intervals_unowned.id}/createRegion/",
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
                self.owned_feature_collection,
                self.owned_bedfile,
                self.owned_intervals,
                self.embedding_data_intervals_wo_thumbnail_data,
            ]
        )
        db.session.commit()
        # make request with forbidden intervall
        response = self.client.post(
            f"/api/embeddingIntervalData/{self.embedding_data_intervals_wo_thumbnail_data.id}/createRegion/",
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
                self.owned_feature_collection,
                self.owned_bedfile,
                self.owned_intervals,
                self.embedding_data_intervals_wo_thumbnail_data,
            ]
        )
        db.session.commit()
        # construct form
        data = {"datasetName": "asdf"}
        # make request with forbidden intervall
        response = self.client.post(
            f"/api/embeddingIntervalData/{self.embedding_data_intervals_wo_thumbnail_data.id}/createRegion/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    def test_cluster_ids_do_not_exist(self):
        """Test whether 404 is returned if clusterID field is None"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        db.session.add_all(
            [
                self.owned_feature_collection,
                self.owned_bedfile,
                self.owned_intervals,
                self.embedding_data_intervals_wo_thumbnail_data,
            ]
        )
        db.session.commit()
        # construct form
        data = {"name": "asdf", "cluster_ids": "[0]"}
        # make request with forbidden intervall
        response = self.client.post(
            f"/api/embeddingIntervalData/{self.embedding_data_intervals_wo_thumbnail_data.id}/createRegion/",
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
                self.owned_feature_collection,
                self.owned_bedfile,
                self.owned_intervals,
                self.embedding_data_owned,
            ]
        )
        db.session.commit()
        # construct form
        data = {"name": "asdf", "cluster_ids": "[1]"}
        # make request with owned interval
        response = self.client.post(
            f"/api/embeddingIntervalData/{self.embedding_data_owned.id}/createRegion/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        # test whether region was created successfully
        self.assertEqual(len(Dataset.query.all()), 2)
        new_dataset = Dataset.query.all()[1]
        self.assertEqual(new_dataset.dataset_name, "asdf")
        self.assertEqual(new_dataset.filetype, "bedfile")
        self.assertEqual(new_dataset.assembly, 1)
        self.assertEqual(new_dataset.perturbation, "none")
        self.assertEqual(new_dataset.sizeType, "Point")
        # test whether subset is correct
        created_subset = pd.read_csv(new_dataset.file_path, sep="\t", header=None)
        expected_subset = self.dummy_regions.iloc[[0, 3, 4], :].reset_index(drop=True)
        expected_subset.columns = [0, 1, 2]
        assert_frame_equal(created_subset, expected_subset)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
