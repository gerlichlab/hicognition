import sys
import unittest
from unittest.mock import patch
import pandas as pd
import numpy as np
from test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
sys.path.append("./")
from app import db
from app.models import Dataset, Intervals, IndividualIntervalData, Assembly, Task
from app.tasks import pipeline_stackup
from app.pipeline_steps import perform_stackup


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
        self.bedfile = Dataset(
            id=1,
            filetype="bedfile"
        )
        self.bigwigfile = Dataset(
            id=2,
            filetype="bigwig"
        )
        # make intervals
        self.intervals1 = Intervals(
            id=1,
            dataset_id=1
        )
        self.intervals2 = Intervals(
            id=1,
            dataset_id=1
        )
        # make tasks
        self.finished_task1 = Task(
            id="test1",
            dataset_id=2,
            intervals_id=1,
            complete=True
        )
        self.unfinished_task1 = Task(
            id="test1",
            dataset_id=2,
            intervals_id=1,
            complete=False
        )

    @patch("app.pipeline_steps._set_task_progress")
    @patch("app.pipeline_steps.perform_stackup")
    def test_dataset_state_not_changed_if_not_last(self, mock_stackup, mock_set_progress):
        """tests whether dataset state is left unchanged if it is not the last task for
        this dataset/intervals combination."""
        # set up database
        self.bedfile.processing_features = [self.bigwigfile]
        db.session.add_all([self.bedfile, self.bigwigfile, self.intervals1, self.unfinished_task1])
        # call pipeline
        pipeline_stackup(2, 1, 10000)
        # check whether processing has finished
        self.assertEqual(self.bedfile.processing_features, [self.bigwigfile])


    @patch("app.pipeline_steps._set_task_progress")
    @patch("app.pipeline_steps.perform_stackup")
    def test_dataset_set_finished_if_last(self, mock_stackup, mock_set_progress):
        """tests whether dataset is set finished correctly if it is the last task for
        this dataset/intervals combination."""
        # set up database
        self.bedfile.processing_features = [self.bigwigfile]
        db.session.add_all([self.bedfile, self.bigwigfile, self.intervals1, self.finished_task1])
        # call pipeline
        pipeline_stackup(2, 1, 10000)
        # check whether processing has finished
        self.assertEqual(len(self.bedfile.processing_features), 0)

    @patch("app.pipeline_steps.log.error")
    @patch("app.pipeline_steps._set_task_progress")
    @patch("app.pipeline_steps.perform_stackup")
    def test_dataset_set_failed_if_failed(self, mock_stackup, mock_set_progress, mock_log):
        """tests whether dataset is set as faild if problem arises."""
        # set up exception raising
        mock_stackup.side_effect = ValueError("Test")
        # set up database
        self.bedfile.processing_features = [self.bigwigfile]
        db.session.add_all([self.bedfile, self.bigwigfile, self.intervals1, self.unfinished_task1])
        # call pipeline
        pipeline_stackup(2, 1, 10000)
        # check whether dataset was added to failed datasets
        self.assertEqual(self.bedfile.failed_features, [self.bigwigfile])
        self.assertEqual(len(self.bedfile.processing_features), 0)
        assert mock_log.called





class TestPerformStackup(LoginTestCase, TempDirTestCase):
    def setUp(self):
        """Add test dataset"""
        # call setUp of LoginTestCase to initialize app
        super(TestPerformStackup, self).setUp()
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token_header
        token_headers = self.get_token_header(token)
        # add content-type
        token_headers["Content-Type"] = "multipart/form-data"
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
        self.intervals1 = Intervals(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            windowsize=200000,
        )
        self.intervals2 = Intervals(
            name="testRegion2",
            dataset_id=2,
            file_path="test_path_2.bedd2db",
            windowsize=50000,
        )
        db.session.add(self.dataset)
        db.session.add(self.dataset2)
        db.session.add(self.intervals1)
        db.session.add(self.intervals2)
        db.session.commit()

    @patch("app.pipeline_steps.bbi.chromsizes")
    @patch("app.pipeline_steps.bbi.stackup")
    @patch("app.pipeline_steps.pd.read_csv")
    def test_stackup_called_correctly_regions_start_end(
        self, mock_read_csv, mock_stackup, mock_chromsizes
    ):
        """Tests whether regions that are defined as chrom, start, end are handled correctly."""
        BIN_NUMBER = 40
        mock_chromsizes.return_value = {"chr1": "test"}
        mock_stackup.return_value = np.empty((2, BIN_NUMBER))
        test_df_interval = pd.DataFrame(
            {0: ["chr1", "chr1"], 1: [0, 1000], 2: [1000, 2000]}
        )
        mock_read_csv.return_value = test_df_interval
        # dispatch call
        dataset_id = 1
        intervals_id = 1
        with patch("app.pipeline_steps.np.load") as mock_load:
            mock_load.return_value = np.array([0, 1])
            perform_stackup(dataset_id, intervals_id, 10000)
        # check whether stackup was called correctly
        mock_stackup.assert_called_with(
            self.dataset.file_path,
            chroms=["chr1", "chr1"],
            starts=[-199500, -198500],
            ends=[200500, 201500],
            bins=BIN_NUMBER,
            missing=np.nan,
        )

    @patch("app.pipeline_steps.bbi.chromsizes")
    @patch("app.pipeline_steps.bbi.stackup")
    @patch("app.pipeline_steps.pd.read_csv")
    def test_stackup_called_correctly_regions_pos(
        self, mock_read_csv, mock_stackup, mock_chromsizes
    ):
        """Tests whether regions that are defined as chrom, pos are handled correctly."""
        BIN_NUMBER = 40
        mock_chromsizes.return_value = {"chr1": "test"}
        mock_stackup.return_value = np.empty((2, BIN_NUMBER))
        test_df_interval = pd.DataFrame({0: ["chr1", "chr1"], 1: [500, 1500]})
        mock_read_csv.return_value = test_df_interval
        # dispatch call
        dataset_id = 1
        intervals_id = 1
        with patch("app.pipeline_steps.np.load") as mock_load:
            mock_load.return_value = np.array([0, 1])
            perform_stackup(dataset_id, intervals_id, 10000)
        # check whether stackup was called correctly
        mock_stackup.assert_called_with(
            self.dataset.file_path,
            chroms=["chr1", "chr1"],
            starts=[-199500, -198500],
            ends=[200500, 201500],
            bins=BIN_NUMBER,
            missing=np.nan,
        )

    @patch("app.pipeline_steps.pd.read_csv")
    def test_small_example_processed_correctly(
        self,
        mock_read_csv,
    ):
        """Tests whether small example stackup is calculated correctly"""
        test_df_interval = pd.DataFrame(
            {
                "chrom": ["chr1", "chr1"],
                "start": [100000, 500000],
                "end": [200000, 600000],
            }
        )
        mock_read_csv.return_value = test_df_interval
        # dispatch call
        dataset_id = 2
        intervals_id = 2
        with patch("app.pipeline_steps.np.load") as mock_load:
            mock_load.return_value = np.array([0])
            perform_stackup(
                dataset_id, intervals_id, 50000
            )  # intervals have a windowsize of 50kb, with binsize of 50kb, this will produce 2 values per example
        # check whether example is correct
        file_path = IndividualIntervalData.query.get(
            1
        ).file_path  # filepath of stackup file
        loaded_dataset = np.load(file_path)
        expected_dataset = np.array([[5.0, 0.0], [6.0, 0.0]])
        self.assertTrue(np.all(np.isclose(loaded_dataset, expected_dataset)))
        # check whether small example is correct
        file_path_small = IndividualIntervalData.query.get(
            1
        ).file_path_small  # filepath of stackup file
        loaded_dataset = np.load(file_path_small)
        expected_dataset = np.array([[5.0, 0.0]])
        self.assertTrue(np.all(np.isclose(loaded_dataset, expected_dataset)))

    @patch("app.pipeline_steps.pd.read_csv")
    def test_regions_with_wrong_chromosomes_skipped_correctly(
        self,
        mock_read_csv,
    ):
        """Tests whether large regions with wrong chromosome names (not in bigwig) are skipped correclty """
        test_df_interval = pd.DataFrame(
            {
                "chrom": ["chr1", "chrT", "chr1", "chrU"],
                "start": [100000, 50000, 500000, 1234],
                "end": [200000, 50000, 600000, 5678],
            }
        )
        mock_read_csv.return_value = test_df_interval
        # dispatch call
        dataset_id = 2
        intervals_id = 2
        with patch("app.pipeline_steps.np.load") as mock_load:
            mock_load.return_value = np.array([0, 1])
            perform_stackup(
                dataset_id, intervals_id, 50000
            )  # intervalrs has a windowsize of 50kb, with binsize of 50kb, this will produce 2 values per example
        # check whether example is correct
        file_path = IndividualIntervalData.query.get(
            1
        ).file_path  # filepath of stackup file
        loaded_dataset = np.load(file_path)
        expected_dataset = np.array(
            [[5.0, 0.0], [np.nan, np.nan], [6.0, 0.0], [np.nan, np.nan]]
        )
        np.testing.assert_array_almost_equal(loaded_dataset, expected_dataset)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
