import sys
import os
import unittest
from unittest.mock import patch
import numpy as np
from test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
sys.path.append("./")
from app import db
from app.models import (
    Dataset,
    Intervals,
    Collection,
    IndividualIntervalData,
    EmbeddingIntervalData,
)
from app.tasks import pipeline_embedding_1d
from app.pipeline_steps import perform_1d_embedding


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
        )

    @patch("app.pipeline_steps.perform_stackup")
    @patch("app.pipeline_steps.perform_1d_embedding")
    def test_stackups_triggered_if_they_dont_exist(self, mock_embedding, mock_stackup):
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


class TestPerformEmbedding1d(LoginTestCase, TempDirTestCase):
    """Tests whether pipeline step perform_1d_embedding is called correctly."""

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
            file_path_small=data_path_1,
        )
        self.ind_data_2 = IndividualIntervalData(
            id=2,
            dataset_id=self.feature_2.id,
            intervals_id=self.intervals_1.id,
            binsize=10000,
            file_path_small=data_path_2,
        )
        self.ind_data_3 = IndividualIntervalData(
            id=3,
            dataset_id=self.feature_3.id,
            intervals_id=self.intervals_1.id,
            binsize=10000,
            file_path_small=data_path_3,
        )

    def test_dastabase_entry_added_correctly(self):
        """Tests whether database entry is added correctly"""
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
        perform_1d_embedding(self.collection_1.id, self.intervals_1.id, 10000)
        # test whether database entry has been added
        embeddings = EmbeddingIntervalData.query.all()
        self.assertEqual(len(embeddings), 1)
        # test whehter addition is correct
        embedding = embeddings[0]
        self.assertEqual(embedding.binsize, 10000)
        self.assertEqual(embedding.value_type, "1d-embedding")
        self.assertEqual(embedding.collection_id, self.collection_1.id)
        self.assertEqual(embedding.intervals_id, self.intervals_1.id)

    def test_correct_embedding_produced(self):
        """Tests whether database entry is added correctly"""
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
        perform_1d_embedding(self.collection_1.id, self.intervals_1.id, 10000)
        # test whether database entry has been added
        embeddings = EmbeddingIntervalData.query.all()
        # test whether dataset is correct
        embedding = embeddings[0]
        data = np.load(embedding.file_path)
        expected = np.array(
            [
                [9.005026, -19.724148],
                [8.464312, -20.689943],
                [9.376196, -22.456],
                [9.890633, -19.460945],
                [10.471338, -22.216688],
                [8.601276, -22.058147],
                [9.632968, -20.021662],
                [9.211276, -20.681519],
                [9.928377, -21.786366],
                [10.563622, -19.949081],
                [10.5394335, -21.080627],
                [9.414719, -21.755327],
                [10.064036, -20.341558],
                [9.769243, -21.013653],
                [8.984867, -21.444807],
            ],
            dtype=np.float32,
        )
        self.assertTrue(np.array_equal(data, expected))

if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
