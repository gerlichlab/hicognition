"""Module with the tests for the stackup creation realted tasks."""
import unittest
from unittest.mock import patch
import pandas as pd
import numpy as np
from tests.test_utils.test_helpers import LoginTestCase, TempDirTestCase
from hicognition import interval_operations

# add path to import app
# import sys
# sys.path.append("./")
from app import db
from app.models import Dataset, Intervals, Assembly, Task
from app.tasks import pipeline_stackup
from app.pipeline_steps import stackup_pipeline_step

from app.pipeline_worker_functions import (
    _do_stackup_fixed_size,
    _do_stackup_variable_size,
)


class TestPipelineStackup(LoginTestCase):
    """Tests for pipeline stackup"""

    def setUp(self):
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
        # make datasets
        self.bedfile = Dataset(id=1, filetype="bedfile")
        self.bigwigfile = Dataset(id=2, filetype="bigwig")
        # make intervals
        self.intervals1 = Intervals(id=1, dataset_id=1)
        self.intervals2 = Intervals(id=1, dataset_id=1)
        # make tasks
        self.finished_task1 = Task(
            id="test1", dataset_id=2, intervals_id=1, complete=True
        )
        self.unfinished_task1 = Task(
            id="test1", dataset_id=2, intervals_id=1, complete=False
        )

    @patch("app.pipeline_steps.set_task_progress")
    @patch("app.pipeline_steps.stackup_pipeline_step")
    def test_dataset_state_not_changed_if_not_last(
        self, mock_stackup, mock_set_progress
    ):
        """tests whether dataset state is left unchanged if it is not the last task for
        this dataset/intervals combination."""
        # set up database
        self.bedfile.processing_features = [self.bigwigfile]
        db.session.add_all(
            [self.bedfile, self.bigwigfile, self.intervals1, self.unfinished_task1]
        )
        # call pipeline
        pipeline_stackup(2, 1, 10000)
        # check whether processing has finished
        self.assertEqual(self.bedfile.processing_features, [self.bigwigfile])

    @patch("app.pipeline_steps.set_task_progress")
    @patch("app.pipeline_steps.stackup_pipeline_step")
    def test_dataset_set_finished_if_last(self, mock_stackup, mock_set_progress):
        """tests whether dataset is set finished correctly if it is the last task for
        this dataset/intervals combination."""
        # set up database
        self.bedfile.processing_features = [self.bigwigfile]
        db.session.add_all(
            [self.bedfile, self.bigwigfile, self.intervals1, self.finished_task1]
        )
        # call pipeline
        pipeline_stackup(2, 1, 10000)
        # check whether processing has finished
        self.assertEqual(len(self.bedfile.processing_features), 0)

    @patch("app.pipeline_steps.log.error")
    @patch("app.pipeline_steps.set_task_progress")
    @patch("app.pipeline_steps.stackup_pipeline_step")
    def test_dataset_set_failed_if_failed(
        self, mock_stackup, mock_set_progress, mock_log
    ):
        """tests whether dataset is set as faild if problem arises."""
        # set up exception raising
        mock_stackup.side_effect = ValueError("Test")
        # set up database
        self.bedfile.processing_features = [self.bigwigfile]
        db.session.add_all(
            [self.bedfile, self.bigwigfile, self.intervals1, self.unfinished_task1]
        )
        # call pipeline
        pipeline_stackup(2, 1, 10000)
        # check whether dataset was added to failed datasets
        self.assertEqual(self.bedfile.failed_features, [self.bigwigfile])
        self.assertEqual(len(self.bedfile.processing_features), 0)
        assert mock_log.called


class TestStackupPipelineStep(LoginTestCase, TempDirTestCase):
    """Tests for stackup pipeline step"""

    def setUp(self):
        """Add test dataset"""
        # call setUp of LoginTestCase to initialize app
        super().setUp()
        # add dataset
        self.dataset = Dataset(
            dataset_name="test3",
            file_path="/test/path/test3.bw",
            filetype="bigwig",
            processing_state="finished",
            user_id=1,
        )
        self.dataset2 = Dataset(
            dataset_name="test4",
            file_path="./tests/testfiles/test.bw",
            filetype="bigwig",
            processing_state="finished",
            user_id=1,
        )
        # add intervals
        self.intervals1 = Intervals(name="testRegion1", dataset_id=1, windowsize=200000)
        self.intervals2 = Intervals(name="testRegion2", dataset_id=2, windowsize=None)
        db.session.add(self.dataset)
        db.session.add(self.dataset2)
        db.session.add(self.intervals1)
        db.session.add(self.intervals2)
        db.session.commit()

    @patch("app.pipeline_steps.worker_funcs._do_stackup_fixed_size")
    @patch("app.pipeline_steps.worker_funcs._do_stackup_variable_size")
    @patch("app.pipeline_steps.pd.read_csv")
    def test_correct_worker_called_fixed_size(
        self, mock_read_csv, mock_variable_size, mock_fixed_size
    ):
        """tests whether correct stackup function is called if
        intervals are of fixed size."""
        test_df_interval = pd.DataFrame(
            {
                "chrom": ["chr1", "chr1"],
                "start": [100000, 500000],
                "end": [200000, 600000],
            }
        )
        mock_read_csv.return_value = test_df_interval
        with patch("app.pipeline_steps.np.load") as mock_load:
            mock_load.return_value = np.array([0, 1])
            stackup_pipeline_step(self.dataset.id, self.intervals1.id, 10000)
        # check whether correct functions were called
        mock_variable_size.assert_not_called()
        mock_fixed_size.assert_called()

    @patch("app.pipeline_steps.worker_funcs._do_stackup_fixed_size")
    @patch("app.pipeline_steps.worker_funcs._do_stackup_variable_size")
    @patch("app.pipeline_steps.pd.read_csv")
    def test_correct_worker_called_variable_size(
        self, mock_read_csv, mock_variable_size, mock_fixed_size
    ):
        """tests whether correct stackup function is called if
        intervals are of fixed size."""
        test_df_interval = pd.DataFrame(
            {
                "chrom": ["chr1", "chr1"],
                "start": [100000, 500000],
                "end": [200000, 600000],
            }
        )
        mock_read_csv.return_value = test_df_interval
        with patch("app.pipeline_steps.np.load") as mock_load:
            mock_load.return_value = np.array([0, 1])
            stackup_pipeline_step(self.dataset.id, self.intervals2.id, 10000)
        # check whether correct functions were called
        mock_variable_size.assert_called()
        mock_fixed_size.assert_not_called()


class TestStackupWorkerFunctionFixedSize(LoginTestCase, TempDirTestCase):
    """Tests worker function for stackup with fixed size"""

    def setUp(self):
        """Add test dataset"""
        # call setUp of LoginTestCase to initialize app
        super().setUp()
        # add dataset
        self.dataset = Dataset(
            dataset_name="test3",
            file_path="/test/path/test3.bw",
            filetype="bigwig",
            processing_state="finished",
            user_id=1,
        )
        self.dataset2 = Dataset(
            dataset_name="test4",
            file_path="./tests/testfiles/test.bw",
            filetype="bigwig",
            processing_state="finished",
            user_id=1,
        )
        db.session.add(self.dataset)
        db.session.add(self.dataset2)
        db.session.commit()

    @patch("app.pipeline_worker_functions.bbi.chromsizes")
    @patch("app.pipeline_worker_functions.bbi.stackup")
    def test_bbi_called_correctly(self, mock_stackup, mock_chromsizes):
        """Tests whether bbi is called with correct parameters"""
        BIN_NUMBER = 40
        mock_chromsizes.return_value = {"chr1": "test"}
        mock_stackup.return_value = np.empty((2, BIN_NUMBER))
        regions = pd.DataFrame({0: ["chr1", "chr1"], 1: [0, 1000], 2: [1000, 2000]})
        # dispatch call
        _do_stackup_fixed_size(self.dataset.file_path, regions, 200000, 10000)
        # check whether stackup was called correctly
        mock_stackup.assert_called_with(
            self.dataset.file_path,
            chroms=["chr1", "chr1"],
            starts=[-199500, -198500],
            ends=[200500, 201500],
            bins=BIN_NUMBER,
            missing=np.nan,
        )

    def test_small_example_processed_correctly(self):
        """Tests whether small example stackup is calculated correctly"""
        regions = pd.DataFrame(
            {
                "chrom": ["chr1", "chr1"],
                "start": [100000, 500000],
                "end": [200000, 600000],
            }
        )
        # dispatch call
        result = _do_stackup_fixed_size(self.dataset2.file_path, regions, 50000, 50000)
        # check result
        expected_dataset = np.array([[5.0, 0.0], [6.0, 0.0]])
        self.assertTrue(np.all(np.isclose(result, expected_dataset)))

    def test_regions_with_wrong_chromosomes_skipped_correctly(self):
        """Tests whether large regions with wrong chromosome names (not in bigwig) are skipped correclty"""
        regions = pd.DataFrame(
            {
                "chrom": ["chr1", "chrT", "chr1", "chrU"],
                "start": [100000, 50000, 500000, 1234],
                "end": [200000, 50000, 600000, 5678],
            }
        )
        # dispatch call
        result = _do_stackup_fixed_size(self.dataset2.file_path, regions, 50000, 50000)
        # check result
        expected_dataset = np.array(
            [[5.0, 0.0], [np.nan, np.nan], [6.0, 0.0], [np.nan, np.nan]]
        )
        np.testing.assert_array_almost_equal(result, expected_dataset)


class TestStackupWorkerFunctionVariableSize(LoginTestCase, TempDirTestCase):
    """Tests worker function for stackup with variable size"""

    def setUp(self):
        """Add test dataset"""
        # call setUp of LoginTestCase to initialize app
        super().setUp()
        # add dataset
        self.dataset = Dataset(
            dataset_name="test3",
            file_path="/test/path/test3.bw",
            filetype="bigwig",
            processing_state="finished",
            user_id=1,
        )
        self.dataset2 = Dataset(
            dataset_name="test4",
            file_path="./tests/testfiles/test.bw",
            filetype="bigwig",
            processing_state="finished",
            user_id=1,
        )
        db.session.add(self.dataset)
        db.session.add(self.dataset2)
        db.session.commit()

    @patch("app.pipeline_worker_functions.bbi.chromsizes")
    @patch("app.pipeline_worker_functions.bbi.stackup")
    def test_bbi_called_correctly(self, mock_stackup, mock_chromsizes):
        """Tests whether bbi is called with correct parameters"""
        bin_number = interval_operations.get_bin_number_for_expanded_intervals(10, 0.2)
        mock_chromsizes.return_value = {"chr1": "test"}
        mock_stackup.return_value = np.empty((2, bin_number))
        regions = pd.DataFrame({0: ["chr1", "chr1"], 1: [0, 1000], 2: [1000, 2000]})
        expanded_regions = interval_operations.expand_regions(
            regions.rename(columns={0: "chrom", 1: "start", 2: "end"}), 0.2
        )
        # dispatch call
        _do_stackup_variable_size(self.dataset.file_path, regions, 10)
        # check whether stackup was called correctly
        mock_stackup.assert_called_with(
            self.dataset.file_path,
            chroms=expanded_regions["chrom"].to_list(),
            starts=expanded_regions["start"].to_list(),
            ends=expanded_regions["end"].to_list(),
            bins=bin_number,
            missing=np.nan,
        )


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
