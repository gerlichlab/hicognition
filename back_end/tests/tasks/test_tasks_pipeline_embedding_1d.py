"""Module with the tests for the 1D-data embedding preprocessing realted tasks."""
import sys
import os
import unittest
from unittest import mock
from unittest.mock import patch
import numpy as np
from hicognition.test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
sys.path.append("./")
from app import db
from app.models import (
    Dataset,
    Intervals,
    Collection,
    IndividualIntervalData,
    EmbeddingIntervalData,
    Assembly,
    Task,
)
from app.tasks import pipeline_embedding_1d
from app.pipeline_steps import embedding_1d_pipeline_step
from app.pipeline_worker_functions import (
    _do_embedding_1d_fixed_size,
    _do_embedding_1d_variable_size,
)


class TestPipelineEmbedding1d(LoginTestCase, TempDirTestCase):
    """Tests whether steps of pipeline are called correctly"""

    def _create_empty_file_in_tempdir(self, file_name):
        file_path = os.path.join(self.TEMP_PATH, file_name)
        open(file_path, "w").close()
        return file_path

    def setUp(self):
        """Add test dataset"""
        # call setUp of LoginTestCase to initialize app
        super().setUp()
        # add assembly
        self.hg19 = Assembly(
            id=1,
            name="hg19",
            chrom_sizes=self.app.config["CHROM_SIZES"],
            chrom_arms=self.app.config["CHROM_ARMS"],
        )
        db.session.add(self.hg19)
        db.session.commit()
        # create bed dataset
        self.bed_file = Dataset(
            id=1, user_id=1, filetype="bedfile", assembly=1, dataset_name="test"
        )
        # create intervals
        self.intervals_1 = Intervals(id=1, windowsize=100000, dataset_id=1)
        # create feature datasets
        self.feature_1 = Dataset(id=2, user_id=1, filetype="bigwig", assembly=1)
        self.feature_2 = Dataset(id=3, user_id=1, filetype="bigwig", assembly=1)
        self.feature_3 = Dataset(id=4, user_id=1, filetype="bigwig", assembly=1)
        # create collection
        self.collection_1 = Collection(
            id=1,
            datasets=[self.feature_1, self.feature_2, self.feature_3],
            kind="1d-features",
            name="test",
        )
        # create stackups
        self.ind_data_1 = IndividualIntervalData(
            id=1,
            dataset_id=self.feature_1.id,
            intervals_id=self.intervals_1.id,
            binsize=10000,
        )
        # add tasks
        self.finished_task1 = Task(
            id="test1", collection_id=1, intervals_id=1, complete=True
        )
        self.unfinished_task1 = Task(
            id="test1", collection_id=1, intervals_id=1, complete=False
        )

    @patch("app.pipeline_steps.set_collection_finished")
    @patch("app.pipeline_steps.set_task_progress")
    @patch("app.pipeline_steps.stackup_pipeline_step")
    @patch("app.pipeline_steps.embedding_1d_pipeline_step")
    def test_stackups_triggered_if_they_dont_exist(
        self, mock_embedding, mock_stackup, mock_set_progress, mock_set_finished
    ):
        """Test if stackups are retriggered if they do not exist for a given parameters combination"""
        # add data to database
        db.session.add_all(
            [
                self.bed_file,
                self.intervals_1,
                self.feature_1,
                self.feature_2,
                self.feature_3,
                self.collection_1,
                self.ind_data_1,
            ]
        )
        # trigger embedding
        pipeline_embedding_1d(self.collection_1.id, self.intervals_1.id, 10000)
        # assert that perform stackup was called with right parameters
        expected_calls = [
            (ds_id, 1, 10000) for ds_id in [self.feature_2.id, self.feature_3.id]
        ]
        for args in expected_calls:
            mock_stackup.assert_any_call(*args)
        # check whether perform embedding is called correctly
        mock_embedding.assert_called_with(
            self.collection_1.id, self.intervals_1.id, 10000
        )
        # trigger embedding with different binsize -> all stackups should be retriggered
        pipeline_embedding_1d(self.collection_1.id, self.intervals_1.id, 20000)
        # assert that perform stackup was called with right parameters
        expected_calls = [
            (ds_id, 1, 20000)
            for ds_id in [self.feature_1.id, self.feature_2.id, self.feature_3.id]
        ]
        for args in expected_calls:
            mock_stackup.assert_any_call(*args)
        # check whether perform embedding is called correctly
        mock_embedding.assert_called_with(
            self.collection_1.id, self.intervals_1.id, 20000
        )

    @patch("app.pipeline_steps.set_task_progress")
    @patch("app.pipeline_steps.stackup_pipeline_step")
    @patch("app.pipeline_steps.embedding_1d_pipeline_step")
    def test_dataset_state_not_changed_if_not_last(
        self, mock_embedding, mock_stackup, mock_progress
    ):
        """tests whether dataset state is left unchanged if it is not the last task for
        this dataset/intervals combination."""
        # set up database
        self.bed_file.processing_collections = [self.collection_1]
        db.session.add_all(
            [self.bed_file, self.collection_1, self.intervals_1, self.unfinished_task1]
        )
        # call pipeline
        pipeline_embedding_1d(1, 1, 10000)
        # check whether processing has finished
        self.assertEqual(self.bed_file.processing_collections, [self.collection_1])

    @patch("app.pipeline_steps.set_task_progress")
    @patch("app.pipeline_steps.stackup_pipeline_step")
    @patch("app.pipeline_steps.embedding_1d_pipeline_step")
    def test_dataset_set_finished_if_last(
        self, mock_embedding, mock_stackup, mock_progress
    ):
        """tests whether dataset is set finished correctly if it is the last task for
        this dataset/intervals combination."""
        # set up database
        self.bed_file.processing_collections = [self.collection_1]
        db.session.add_all(
            [self.bed_file, self.collection_1, self.intervals_1, self.finished_task1]
        )
        # call pipeline
        pipeline_embedding_1d(1, 1, 10000)
        # check whether processing has finished
        self.assertEqual(self.bed_file.processing_collections, [])

    @patch("app.pipeline_steps.log.error")
    @patch("app.pipeline_steps.set_task_progress")
    @patch("app.pipeline_steps.stackup_pipeline_step")
    @patch("app.pipeline_steps.embedding_1d_pipeline_step")
    def test_dataset_set_failed_if_failed(
        self, mock_embedding, mock_stackup, mock_progress, mock_log
    ):
        """tests whether dataset is set as faild if problem arises."""
        # set up exception raising
        mock_embedding.side_effect = ValueError("Test")
        # set up database
        self.bed_file.processing_collections = [self.collection_1]
        db.session.add_all(
            [self.bed_file, self.collection_1, self.intervals_1, self.finished_task1]
        )
        # call pipeline
        pipeline_embedding_1d(1, 1, 10000)
        # check whether processing has finished
        self.assertEqual(self.bed_file.failed_collections, [self.collection_1])
        self.assertEqual(self.bed_file.processing_collections, [])
        assert mock_log.called


class TestEmbedding1DPipelineStep(LoginTestCase, TempDirTestCase):
    """Tests embedding 1d pipeline step"""

    def setUp(self):
        """Add test dataset"""
        # call setUp of LoginTestCase to initialize app
        super().setUp()
        # create dummy data
        ingredient_1 = np.array([[1, 2, 3], [5, 6, 7], [9, 10, 11]])
        self.test_data_1 = np.concatenate([ingredient_1] * 5)
        data_path_1 = os.path.join(self.TEMP_PATH, "data1.npy")
        np.save(data_path_1, self.test_data_1)
        ingredient_2 = np.array([[0.1, 0.2, 0.3], [0.5, 0.6, 0.7], [0.9, 0.10, 0.11]])
        self.test_data_2 = np.concatenate([ingredient_2] * 5)
        data_path_2 = os.path.join(self.TEMP_PATH, "data2.npy")
        np.save(data_path_2, self.test_data_2)
        ingredient_3 = np.array([[0.2, 0.3, 0.4], [0.6, 0.7, 0.8], [1, 1.1, 1.1]])
        self.test_data_3 = np.concatenate([ingredient_3] * 5)
        data_path_3 = os.path.join(self.TEMP_PATH, "data3.npy")
        np.save(data_path_3, self.test_data_3)
        # add database entries
        # create bed dataset
        self.bed_file = Dataset(id=1, user_id=1, filetype="bedfile")
        # create intervals
        self.intervals_1 = Intervals(id=1, windowsize=100000, dataset_id=1)
        self.intervals_2 = Intervals(id=2, windowsize=None, dataset_id=1)
        # create feature datasets
        self.feature_1 = Dataset(id=2, user_id=1, filetype="bigwig")
        self.feature_2 = Dataset(id=3, user_id=1, filetype="bigwig")
        self.feature_3 = Dataset(id=4, user_id=1, filetype="bigwig")
        # create collection
        self.collection_1 = Collection(
            id=1, datasets=[self.feature_1, self.feature_2, self.feature_3]
        )
        # create stackups
        self.ind_data_1 = IndividualIntervalData(
            id=1,
            dataset_id=self.feature_1.id,
            intervals_id=self.intervals_1.id,
            binsize=10000,
            file_path=data_path_1,
        )
        self.ind_data_2 = IndividualIntervalData(
            id=2,
            dataset_id=self.feature_2.id,
            intervals_id=self.intervals_1.id,
            binsize=10000,
            file_path=data_path_2,
        )
        self.ind_data_3 = IndividualIntervalData(
            id=3,
            dataset_id=self.feature_3.id,
            intervals_id=self.intervals_1.id,
            binsize=10000,
            file_path=data_path_3,
        )

    @patch("app.pipeline_steps.worker_funcs._do_embedding_1d_variable_size")
    @patch("app.pipeline_steps.worker_funcs._do_embedding_1d_fixed_size")
    def test_database_entry_added_correctly(self, mock_fixed_size, mock_variable_size):
        """Tests whether database entry is added correctly"""
        # add return values
        mock_fixed_size.return_value = {
            "embedding": np.full((1, 1), 1),
            "clusters": {
                "large": {
                    "cluster_ids": np.full((1, 1), 2),
                    "average_values": np.full((1, 1), 3),
                },
                "small": {
                    "cluster_ids": np.full((1, 1), 4),
                    "average_values": np.full((1, 1), 5),
                },
            },
            "features": np.full((1, 1), 6),
        }
        mock_variable_size.return_value = {
            "embedding": np.full((1, 1), 1),
            "clusters": {
                "large": {
                    "cluster_ids": np.full((1, 1), 2),
                    "average_values": np.full((1, 1), 3),
                },
                "small": {
                    "cluster_ids": np.full((1, 1), 4),
                    "average_values": np.full((1, 1), 5),
                },
            },
            "features": np.full((1, 1), 6),
        }
        # add data to database
        db.session.add_all(
            [
                self.bed_file,
                self.intervals_1,
                self.feature_1,
                self.feature_2,
                self.feature_3,
                self.collection_1,
                self.ind_data_1,
                self.ind_data_2,
                self.ind_data_3,
            ]
        )
        embedding_1d_pipeline_step(self.collection_1.id, self.intervals_1.id, 10000)
        # test whether database entry has been added
        embeddings = EmbeddingIntervalData.query.all()
        self.assertEqual(len(embeddings), 2)
        self.assertEqual(
            {"small", "large"}, set([emb.cluster_number for emb in embeddings])
        )
        # test whehter addition is correct
        embedding = embeddings[0]
        self.assertEqual(embedding.binsize, 10000)
        self.assertEqual(embedding.value_type, "1d-embedding")
        self.assertEqual(embedding.collection_id, self.collection_1.id)
        self.assertEqual(embedding.intervals_id, self.intervals_1.id)
        embedding = embeddings[1]
        self.assertEqual(embedding.binsize, 10000)
        self.assertEqual(embedding.value_type, "1d-embedding")
        self.assertEqual(embedding.collection_id, self.collection_1.id)
        self.assertEqual(embedding.intervals_id, self.intervals_1.id)

    @patch("app.pipeline_steps.worker_funcs._do_embedding_1d_variable_size")
    @patch("app.pipeline_steps.worker_funcs._do_embedding_1d_fixed_size")
    def test_correct_worker_called_fixed_size_intervals(
        self, mock_fixed_size, mock_variable_size
    ):
        """Tests whether correct worker function is called with fixed size intervals"""
        # add return values
        mock_fixed_size.return_value = {
            "embedding": np.full((1, 1), 1),
            "clusters": {
                "large": {
                    "cluster_ids": np.full((1, 1), 2),
                    "average_values": np.full((1, 1), 3),
                },
                "small": {
                    "cluster_ids": np.full((1, 1), 4),
                    "average_values": np.full((1, 1), 5),
                },
            },
            "features": np.full((1, 1), 6),
        }
        mock_variable_size.return_value = {
            "embedding": np.full((1, 1), 1),
            "clusters": {
                "large": {
                    "cluster_ids": np.full((1, 1), 2),
                    "average_values": np.full((1, 1), 3),
                },
                "small": {
                    "cluster_ids": np.full((1, 1), 4),
                    "average_values": np.full((1, 1), 5),
                },
            },
            "features": np.full((1, 1), 6),
        }
        # add data to database
        db.session.add_all(
            [
                self.bed_file,
                self.intervals_1,
                self.feature_1,
                self.feature_2,
                self.feature_3,
                self.collection_1,
                self.ind_data_1,
                self.ind_data_2,
                self.ind_data_3,
            ]
        )
        embedding_1d_pipeline_step(self.collection_1.id, self.intervals_1.id, 10000)
        # test whether correct workerfunction was called
        mock_fixed_size.assert_called()
        mock_variable_size.assert_not_called()

    @patch("app.pipeline_steps.worker_funcs._do_embedding_1d_variable_size")
    @patch("app.pipeline_steps.worker_funcs._do_embedding_1d_fixed_size")
    def test_correct_worker_called_variable_size_intervals(
        self, mock_fixed_size, mock_variable_size
    ):
        """Tests whether correct worker function is called with fixed size intervals"""
        # add return values
        mock_fixed_size.return_value = {
            "embedding": np.full((1, 1), 1),
            "clusters": {
                "large": {
                    "cluster_ids": np.full((1, 1), 2),
                    "average_values": np.full((1, 1), 3),
                },
                "small": {
                    "cluster_ids": np.full((1, 1), 4),
                    "average_values": np.full((1, 1), 5),
                },
            },
            "features": np.full((1, 1), 6),
        }
        mock_variable_size.return_value = {
            "embedding": np.full((1, 1), 1),
            "clusters": {
                "large": {
                    "cluster_ids": np.full((1, 1), 2),
                    "average_values": np.full((1, 1), 3),
                },
                "small": {
                    "cluster_ids": np.full((1, 1), 4),
                    "average_values": np.full((1, 1), 5),
                },
            },
            "features": np.full((1, 1), 6),
        }
        # add data to database
        db.session.add_all(
            [
                self.bed_file,
                self.intervals_1,
                self.intervals_2,
                self.feature_1,
                self.feature_2,
                self.feature_3,
                self.collection_1,
                self.ind_data_1,
                self.ind_data_2,
                self.ind_data_3,
            ]
        )
        embedding_1d_pipeline_step(self.collection_1.id, self.intervals_2.id, 10)
        # test whether correct workerfunction was called
        mock_fixed_size.assert_not_called()
        mock_variable_size.assert_called()


class TestEmbedding1DWorkerFunctionFixedSize(LoginTestCase, TempDirTestCase):
    """Tests fixed size worker function"""

    def setUp(self):
        """Add test dataset"""
        # call setUp of LoginTestCase to initialize app
        super().setUp()
        # create dummy data
        ingredient_1 = np.array([[1, 2, 3], [5, 6, 7], [9, 10, 11]])
        self.test_data_1 = np.concatenate([ingredient_1] * 5)
        data_path_1 = os.path.join(self.TEMP_PATH, "data1.npy")
        np.save(data_path_1, self.test_data_1)
        ingredient_2 = np.array([[0.1, 0.2, 0.3], [0.5, 0.6, 0.7], [0.9, 0.10, 0.11]])
        self.test_data_2 = np.concatenate([ingredient_2] * 5)
        data_path_2 = os.path.join(self.TEMP_PATH, "data2.npy")
        np.save(data_path_2, self.test_data_2)
        ingredient_3 = np.array([[0.2, 0.3, 0.4], [0.6, 0.7, 0.8], [1, 1.1, 1.1]])
        self.test_data_3 = np.concatenate([ingredient_3] * 5)
        data_path_3 = os.path.join(self.TEMP_PATH, "data3.npy")
        np.save(data_path_3, self.test_data_3)
        # add database entries
        # create bed dataset
        self.bed_file = Dataset(id=1, user_id=1, filetype="bedfile")
        # create intervals
        self.intervals_1 = Intervals(id=1, windowsize=100000, dataset_id=1)
        # create feature datasets
        self.feature_1 = Dataset(id=2, user_id=1, filetype="bigwig")
        self.feature_2 = Dataset(id=3, user_id=1, filetype="bigwig")
        self.feature_3 = Dataset(id=4, user_id=1, filetype="bigwig")
        # create collection
        self.collection_1 = Collection(
            id=1, datasets=[self.feature_1, self.feature_2, self.feature_3]
        )
        # create stackups
        self.ind_data_1 = IndividualIntervalData(
            id=1,
            dataset_id=self.feature_1.id,
            intervals_id=self.intervals_1.id,
            binsize=10000,
            file_path=data_path_1,
        )
        self.ind_data_2 = IndividualIntervalData(
            id=2,
            dataset_id=self.feature_2.id,
            intervals_id=self.intervals_1.id,
            binsize=10000,
            file_path=data_path_2,
        )
        self.ind_data_3 = IndividualIntervalData(
            id=3,
            dataset_id=self.feature_3.id,
            intervals_id=self.intervals_1.id,
            binsize=10000,
            file_path=data_path_3,
        )

    def test_correct_features_produced(self):
        """Tests whether produced features are correct"""
        # add smaller cluster sizes
        d = self.app.config.copy()
        d["CLUSTER_NUMBER_LARGE"] = 5
        d["CLUSTER_NUMBER_SMALL"] = 2
        with patch("app.pipeline_worker_functions.current_app.config") as mock_config:
            mock_config.__getitem__.side_effect = d.__getitem__
            # add data to database
            db.session.add_all(
                [
                    self.bed_file,
                    self.intervals_1,
                    self.feature_1,
                    self.feature_2,
                    self.feature_3,
                    self.collection_1,
                    self.ind_data_1,
                    self.ind_data_2,
                    self.ind_data_3,
                ]
            )
            # dispatch call
            embedding_results = _do_embedding_1d_fixed_size(
                self.collection_1.id, self.intervals_1.id, 10000
            )
            # test whether feature frame used is correct
            expected_features = np.array(
                [
                    [2.0, 0.2, 0.3],
                    [6.0, 0.6, 0.7],
                    [10.0, 0.1, 1.1],
                    [2.0, 0.2, 0.3],
                    [6.0, 0.6, 0.7],
                    [10.0, 0.1, 1.1],
                    [2.0, 0.2, 0.3],
                    [6.0, 0.6, 0.7],
                    [10.0, 0.1, 1.1],
                    [2.0, 0.2, 0.3],
                    [6.0, 0.6, 0.7],
                    [10.0, 0.1, 1.1],
                    [2.0, 0.2, 0.3],
                    [6.0, 0.6, 0.7],
                    [10.0, 0.1, 1.1],
                ]
            )
            self.assertTrue(
                np.array_equal(embedding_results["features"], expected_features)
            )


class TestEmbedding1DWorkerFunctionVariableSize(LoginTestCase, TempDirTestCase):
    """Tests variable size worker function"""

    def setUp(self):
        """Add test dataset"""
        # call setUp of LoginTestCase to initialize app
        super().setUp()
        # create dummy data
        ingredient_1 = np.array([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] * 3])
        self.test_data_1 = np.concatenate([ingredient_1] * 5)
        data_path_1 = os.path.join(self.TEMP_PATH, "data1.npy")
        np.save(data_path_1, self.test_data_1)
        ingredient_2 = np.array([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] * 3])
        self.test_data_2 = np.concatenate([ingredient_2] * 5)
        data_path_2 = os.path.join(self.TEMP_PATH, "data2.npy")
        np.save(data_path_2, self.test_data_2)
        ingredient_3 = np.array([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] * 3])
        self.test_data_3 = np.concatenate([ingredient_3] * 5)
        data_path_3 = os.path.join(self.TEMP_PATH, "data3.npy")
        np.save(data_path_3, self.test_data_3)
        # add database entries
        # create bed dataset
        self.bed_file = Dataset(id=1, user_id=1, filetype="bedfile")
        # create intervals
        self.intervals_1 = Intervals(id=1, windowsize=None, dataset_id=1)
        # create feature datasets
        self.feature_1 = Dataset(id=2, user_id=1, filetype="bigwig")
        self.feature_2 = Dataset(id=3, user_id=1, filetype="bigwig")
        self.feature_3 = Dataset(id=4, user_id=1, filetype="bigwig")
        # create collection
        self.collection_1 = Collection(
            id=1, datasets=[self.feature_1, self.feature_2, self.feature_3]
        )
        # create stackups
        self.ind_data_1 = IndividualIntervalData(
            id=1,
            dataset_id=self.feature_1.id,
            intervals_id=self.intervals_1.id,
            binsize=10,
            file_path=data_path_1,
        )
        self.ind_data_2 = IndividualIntervalData(
            id=2,
            dataset_id=self.feature_2.id,
            intervals_id=self.intervals_1.id,
            binsize=10,
            file_path=data_path_2,
        )
        self.ind_data_3 = IndividualIntervalData(
            id=3,
            dataset_id=self.feature_3.id,
            intervals_id=self.intervals_1.id,
            binsize=10,
            file_path=data_path_3,
        )

    def test_correct_features_produced(self):
        """Tests whether produced features are correct"""
        # add smaller cluster sizes
        d = self.app.config.copy()
        d["CLUSTER_NUMBER_LARGE"] = 5
        d["CLUSTER_NUMBER_SMALL"] = 2
        with patch("app.pipeline_worker_functions.current_app.config") as mock_config:
            mock_config.__getitem__.side_effect = d.__getitem__
            # add data to database
            db.session.add_all(
                [
                    self.bed_file,
                    self.intervals_1,
                    self.feature_1,
                    self.feature_2,
                    self.feature_3,
                    self.collection_1,
                    self.ind_data_1,
                    self.ind_data_2,
                    self.ind_data_3,
                ]
            )
            # dispatch call
            embedding_results = _do_embedding_1d_variable_size(
                self.collection_1.id, self.intervals_1.id, 10
            )
            # test whether feature frame used is correct
            expected_features = np.array(
                [
                    [7.5, 7.5, 7.5],
                    [7.5, 7.5, 7.5],
                    [7.5, 7.5, 7.5],
                    [7.5, 7.5, 7.5],
                    [7.5, 7.5, 7.5],
                ]
            )
            self.assertTrue(
                np.array_equal(embedding_results["features"], expected_features)
            )


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
