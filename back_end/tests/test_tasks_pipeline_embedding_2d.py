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
    EmbeddingIntervalData,
    IndividualIntervalData,
    Assembly,
    Task,
)
from app.tasks import pipeline_embedding_2d
from app.pipeline_steps import embedding_2d_pipeline_step
from app.pipeline_worker_functions import (
    _do_embedding_2d_fixed_size,
    _do_embedding_2d_variable_size,
)


class TestPipelineEmbedding2d(LoginTestCase, TempDirTestCase):
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
        self.bed_file = Dataset(id=1, user_id=1, filetype="bedfile", assembly=1)
        # create intervals
        self.intervals_1 = Intervals(id=1, windowsize=100000, dataset_id=1)
        # create feature datasets
        self.feature_1 = Dataset(id=2, user_id=1, filetype="cooler", assembly=1)
        self.feature_2 = Dataset(id=3, user_id=1, filetype="cooler", assembly=1)
        self.feature_3 = Dataset(id=4, user_id=1, filetype="cooler", assembly=1)
        # create collection
        self.collection_1 = Collection(
            id=1, datasets=[self.feature_1, self.feature_2, self.feature_3]
        )
        # add tasks
        self.finished_task1 = Task(
            id="test1", collection_id=1, intervals_id=1, complete=True
        )
        self.unfinished_task1 = Task(
            id="test1", collection_id=1, intervals_id=1, complete=False
        )

    @patch("app.pipeline_steps.set_task_progress")
    @patch("app.pipeline_steps.embedding_2d_pipeline_step")
    def test_dataset_state_not_changed_if_not_last(
        self, mock_embedding, mock_progress
    ):
        """tests whether dataset state is left unchanged if it is not the last task for
        this dataset/intervals combination."""
        # set up database
        self.bed_file.processing_collections = [self.collection_1]
        db.session.add_all(
            [self.bed_file, self.collection_1, self.intervals_1, self.unfinished_task1]
        )
        # call pipeline
        pipeline_embedding_2d(1, 1, 10000)
        # check whether processing has finished
        self.assertEqual(self.bed_file.processing_collections, [self.collection_1])

    @patch("app.pipeline_steps.set_task_progress")
    @patch("app.pipeline_steps.embedding_2d_pipeline_step")
    def test_dataset_set_finished_if_last(
        self, mock_embedding, mock_progress
    ):
        """tests whether dataset is set finished correctly if it is the last task for
        this dataset/intervals combination."""
        # set up database
        self.bed_file.processing_collections = [self.collection_1]
        db.session.add_all(
            [self.bed_file, self.collection_1, self.intervals_1, self.finished_task1]
        )
        # call pipeline
        pipeline_embedding_2d(1, 1, 10000)
        # check whether processing has finished
        self.assertEqual(self.bed_file.processing_collections, [])

    @patch("app.pipeline_steps.log.error")
    @patch("app.pipeline_steps.set_task_progress")
    @patch("app.pipeline_steps.embedding_2d_pipeline_step")
    def test_dataset_set_failed_if_failed(
        self, mock_embedding, mock_progress, mock_log
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
        pipeline_embedding_2d(1, 1, 10000)
        # check whether processing has finished
        self.assertEqual(self.bed_file.failed_collections, [self.collection_1])
        self.assertEqual(self.bed_file.processing_collections, [])
        assert mock_log.called

class TestEmbedding2DPipelineStep(LoginTestCase, TempDirTestCase):
    """Tests embedding 2d pipeline step"""

    def setUp(self):
        """Add test dataset"""
        # call setUp of LoginTestCase to initialize app
        super().setUp()
        # create bed dataset
        self.bed_file = Dataset(id=1, user_id=1, filetype="bedfile")
        # create intervals
        self.intervals_1 = Intervals(id=1, windowsize=100000, dataset_id=1)
        self.intervals_2 = Intervals(id=2, windowsize=None, dataset_id=1)
        # create feature datasets
        self.feature_1 = Dataset(id=2, user_id=1, filetype="cooler")
        self.feature_2 = Dataset(id=3, user_id=1, filetype="cooler")
        self.feature_3 = Dataset(id=4, user_id=1, filetype="cooler")
        # create collection
        self.collection_1 = Collection(
            id=1, datasets=[self.feature_1, self.feature_2, self.feature_3]
        )

    @patch("app.pipeline_steps.worker_funcs._do_embedding_2d_variable_size")
    @patch("app.pipeline_steps.worker_funcs._do_embedding_2d_fixed_size")
    def test_database_entry_added_correctly(self, mock_fixed_size, mock_variable_size):
        """Tests whether database entry is added correctly"""
        # add return values
        mock_fixed_size.return_value = [np.empty((1, 1))] * 4
        mock_variable_size.return_value = [np.empty((1, 1))] * 4
        # add data to database
        db.session.add_all(
            [
                self.bed_file,
                self.intervals_1,
                self.feature_1,
                self.feature_2,
                self.feature_3,
                self.collection_1
            ]
        )
        embedding_2d_pipeline_step(self.collection_1.id, self.intervals_1.id, 10000)
        # test whether database entry has been added
        embeddings = EmbeddingIntervalData.query.all()
        self.assertEqual(len(embeddings), 1)
        # test whehter addition is correct
        embedding = embeddings[0]
        self.assertEqual(embedding.binsize, 10000)
        self.assertEqual(embedding.value_type, "2d-embedding")
        self.assertEqual(embedding.collection_id, self.collection_1.id)
        self.assertEqual(embedding.intervals_id, self.intervals_1.id)

    @patch("app.pipeline_steps.worker_funcs._do_embedding_2d_variable_size")
    @patch("app.pipeline_steps.worker_funcs._do_embedding_2d_fixed_size")
    def test_correct_worker_called_fixed_size_intervals(
        self, mock_fixed_size, mock_variable_size
    ):
        """Tests whether correct worker function is called with fixed size intervals"""
        # add return values
        mock_fixed_size.return_value = [np.empty((1, 1))] * 4
        mock_variable_size.return_value = [np.empty((1, 1))] * 4
        # add data to database
        db.session.add_all(
            [
                self.bed_file,
                self.intervals_1,
                self.feature_1,
                self.feature_2,
                self.feature_3,
                self.collection_1
            ]
        )
        embedding_2d_pipeline_step(self.collection_1.id, self.intervals_1.id, 10000)
        # test whether correct workerfunction was called
        mock_fixed_size.assert_called()
        mock_variable_size.assert_not_called()

    @patch("app.pipeline_steps.worker_funcs._do_embedding_2d_variable_size")
    @patch("app.pipeline_steps.worker_funcs._do_embedding_2d_fixed_size")
    def test_correct_worker_called_variable_size_intervals(
        self, mock_fixed_size, mock_variable_size
    ):
        """Tests whether correct worker function is called with fixed size intervals"""
        # ad return values
        mock_fixed_size.return_value = [np.empty((1, 1))] * 4
        mock_variable_size.return_value = [np.empty((1, 1))] * 4
        # add data to database
        db.session.add_all(
            [
                self.bed_file,
                self.intervals_1,
                self.intervals_2,
                self.feature_1,
                self.feature_2,
                self.feature_3,
                self.collection_1
            ]
        )
        embedding_2d_pipeline_step(self.collection_1.id, self.intervals_2.id, 10)
        # test whether correct workerfunction was called
        mock_fixed_size.assert_not_called()
        mock_variable_size.assert_called()


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
