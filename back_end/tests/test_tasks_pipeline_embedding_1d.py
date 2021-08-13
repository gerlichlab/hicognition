import sys
import os
import unittest
from unittest.mock import patch
import pandas as pd
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
)
from app.tasks import pipeline_embedding_1d


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
        expected_calls = [(ds_id, 1, 10000) for ds_id in [self.feature_2.id, self.feature_3.id]]
        for args in expected_calls:
            mock_stackup.assert_any_call(*args)
        # check whether perform embedding is called correctly
        mock_embedding.assert_called_with(self.collection_1.id, self.intervals_1.id, 10000)
        # trigger embedding with different binsize -> all stackups should be retriggered
        pipeline_embedding_1d(self.collection_1.id, self.intervals_1.id, 20000)
        # assert that perform stackup was called with right parameters
        expected_calls = [(ds_id, 1, 20000) for ds_id in [self.feature_1.id, self.feature_2.id, self.feature_3.id]]
        for args in expected_calls:
            mock_stackup.assert_any_call(*args)
        # check whether perform embedding is called correctly
        mock_embedding.assert_called_with(self.collection_1.id, self.intervals_1.id, 20000)

class TestPerformEmbedding1d(LoginTestCase, TempDirTestCase):
    """Tests whether pipeline step perform_1d_embedding is called correctly."""


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
