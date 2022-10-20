"""Module with the tests for all bed-file preprocessing realted tasks."""
import unittest
from unittest.mock import patch
import pandas as pd
import numpy as np
from hicognition.test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
# sys.path.append("./")
from app import db
from app.models import Dataset, Intervals, Assembly
from app.tasks import pipeline_bed
from app.pipeline_steps import bed_preprocess_pipeline_step


class TestPipelineBed(LoginTestCase, TempDirTestCase):
    """Tests whether pipelin_bed task calls
    the pipeline steps correctly"""

    def setUp(self):
        """Add test dataset"""
        # call setUp of LoginTestCase to initialize app
        super(TestPipelineBed, self).setUp()
        # add assembly
        self.hg19 = Assembly(
            id=1,
            name="hg19",
            chrom_sizes=self.app.config["CHROM_SIZES"],
            chrom_arms=self.app.config["CHROM_ARMS"],
        )
        db.session.add(self.hg19)
        db.session.commit()
        # add dataset
        self.dataset_point = self.create_dataset(
            dataset_name="test3",
            file_path="/test/path/test3.bed",
            filetype="bedfile",
            processing_state="finished",
            user_id=1,
            assembly=1,
            sizeType="Point",
        )
        self.dataset_interval = self.create_dataset(
            dataset_name="test4",
            file_path="/test/path/test4.bed",
            filetype="bedfile",
            processing_state="finished",
            user_id=1,
            assembly=1,
            sizeType="Interval",
        )
        db.session.add(self.dataset_point)
        db.session.add(self.dataset_interval)
        db.session.commit()

    @patch("app.tasks.io_helpers.clean_bed")
    @patch("app.pipeline_steps.set_task_progress")
    @patch("app.pipeline_steps.bed_preprocess_pipeline_step")
    def test_helper_calls_dispatched_correctly_point_feature(
        self, mock_bed_pipeline_step, mock_set_progress, mock_clean_bed
    ):
        """Tests whether the functions that execute the different pipeline steps are called
        correctly for a point feature bedfile."""
        # launch task
        pipeline_bed(1)
        # check whether dataset file_path is now sorted file_path
        self.assertEqual(self.dataset_point.file_path, "/test/path/test3_cleaned.bed")
        # check whether sort_bed was called correctly
        mock_clean_bed.assert_called_with(
            *["/test/path/test3.bed", "/test/path/test3_cleaned.bed"]
        )
        # check whether convert_bed_to_bedpe and bed_pipeline_step was called correctly
        for window in [
            size
            for size in self.app.config["PREPROCESSING_MAP"].keys()
            if size != "variable"
        ]:
            mock_bed_pipeline_step.assert_any_call(*[1, window])
        # check whether set_progress was called with 100 last
        mock_set_progress.assert_called_with(100)

    @patch("app.tasks.io_helpers.clean_bed")
    @patch("app.pipeline_steps.set_task_progress")
    @patch("app.pipeline_steps.bed_preprocess_pipeline_step")
    def test_helper_calls_dispatched_correctly_interval_feature(
        self, mock_bed_pipeline_step, mock_set_progress, mock_clean_bed
    ):
        """Tests whether the functions that execute the different pipeline steps are called
        correctly for an interval feature bedfile."""
        # launch task
        pipeline_bed(2)
        # check whether dataset file_path is now sorted file_path
        self.assertEqual(
            self.dataset_interval.file_path, "/test/path/test4_cleaned.bed"
        )
        # check whether sort_bed was called correctly
        mock_clean_bed.assert_called_with(
            *["/test/path/test4.bed", "/test/path/test4_cleaned.bed"]
        )
        # check whether convert_bed_to_bedpe and bed_pipeline_step was called correctly
        mock_bed_pipeline_step.assert_called_with(2, "variable")
        self.assertEqual(mock_bed_pipeline_step.call_count, 1)
        # check whether set_progress was called with 100 last
        mock_set_progress.assert_called_with(100)


class TestBedPreprocessPipelineStep(LoginTestCase, TempDirTestCase):
    """Tests bed_preprocess_pipeline_step"""

    def setUp(self):
        """Add test dataset"""
        # call setUp of LoginTestCase to initialize app
        super(TestBedPreprocessPipelineStep, self).setUp()
        # add assembly
        self.hg19 = Assembly(
            id=1,
            name="hg19",
            chrom_sizes=self.app.config["CHROM_SIZES"],
            chrom_arms=self.app.config["CHROM_ARMS"],
        )
        db.session.add(self.hg19)
        db.session.commit()
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token_header
        token_headers = self.get_token_header(token)
        # add content-type
        token_headers["Content-Type"] = "multipart/form-data"
        # add dataset
        self.dataset = self.create_dataset(
            dataset_name="test3",
            file_path="/test/path/test3.bed",
            filetype="bedfile",
            processing_state="finished",
            user_id=1,
            assembly=1,
            sizeType="Point",
        )
        self.dataset_interval = self.create_dataset(
            dataset_name="test4",
            file_path="/test/path/test4.bed",
            filetype="bedfile",
            processing_state="finished",
            user_id=1,
            assembly=1,
            sizeType="Interval",
        )
        db.session.add(self.dataset)
        db.session.add(self.dataset_interval)
        db.session.commit()

    @patch("app.tasks.pd.read_csv")
    def test_interval_features_add_correctly(self, mock_read_csv):
        """Tests whether intervals are added correclty if windowsize is variable"""
        mock_frame = pd.DataFrame(
            {0: ["chr1", "chr1", "chr1"], 1: [0, 1, 2], 2: [1, 2, 3]}
        )
        mock_read_csv.return_value = mock_frame
        bed_preprocess_pipeline_step(2, "variable")
        # check whehter associated index file is equally long as regions
        intervals = Intervals.query.first()
        self.assertEqual(intervals.windowsize, None)

    @patch("app.tasks.pd.read_csv")
    def test_point_features_add_correctly(self, mock_read_csv):
        """Tests whether intervals are added correclty if windowsize is constant"""
        mock_frame = pd.DataFrame(
            {0: ["chr1", "chr1", "chr1"], 1: [0, 1, 2], 2: [1, 2, 3]}
        )
        mock_read_csv.return_value = mock_frame
        bed_preprocess_pipeline_step(2, 200000)
        # check whehter associated index file is equally long as regions
        intervals = Intervals.query.first()
        self.assertEqual(intervals.windowsize, 200000)

    @patch("app.tasks.pd.read_csv")
    def test_whether_small_regions_are_not_downsampled(self, mock_read_csv):
        """Tests that if bed preprocess pipeline step is called with small
        regions, they are not downsampled."""
        mock_frame = pd.DataFrame(
            {0: ["chr1", "chr1", "chr1"], 1: [0, 1, 2], 2: [1, 2, 3]}
        )
        mock_read_csv.return_value = mock_frame
        # call function
        window = 400000
        bed_preprocess_pipeline_step(1, window)
        # check whehter associated index file is equally long as regions
        intervals = Intervals.query.first()
        sub_sample_index = np.load(intervals.file_path_sub_sample_index)
        self.assertEqual(len(mock_frame), len(sub_sample_index))

    @patch("app.tasks.pd.read_csv")
    def test_whether_large_regions_are_not_downsampled(self, mock_read_csv):
        """Tests that if bed preprocess pipeline step is called with large
        regions (larger than indicated in config['STACKUP_THRESHOLD']),
        they are downsampled to have length config['STACKUP_THRESHOLD']."""
        mock_frame = pd.DataFrame({0: ["chr1"] * 20, 1: [0] * 20, 2: [1] * 20})
        mock_read_csv.return_value = mock_frame
        # call function
        window = 400000
        bed_preprocess_pipeline_step(1, window)
        # check whehter unique entries in associated index file is equally long as regions
        intervals = Intervals.query.first()
        sub_sample_index = np.load(intervals.file_path_sub_sample_index)
        self.assertEqual(
            self.app.config["STACKUP_THRESHOLD"], len(set(sub_sample_index))
        )


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
