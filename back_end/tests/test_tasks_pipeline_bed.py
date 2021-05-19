from functools import partial
import sys
import unittest
from unittest.mock import patch
from test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
sys.path.append("./")
from app import db
from app.models import Dataset, Intervals
from app.tasks import pipeline_bed
from app.pipeline_steps import bed_preprocess_pipeline_step


class TestPipelineBed(LoginTestCase, TempDirTestCase):
    """Tests whether pipelin_bed task calls
    the pipeline steps correctly"""

    def setUp(self):
        """Add test dataset"""
        # call setUp of LoginTestCase to initialize app
        super(TestPipelineBed, self).setUp()
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token_header
        token_headers = self.get_token_header(token)
        # add content-type
        token_headers["Content-Type"] = "multipart/form-data"
        # add dataset
        self.dataset = Dataset(
            dataset_name="test3",
            file_path="/test/path/test3.bed",
            filetype="bedfile",
            processing_state="finished",
            user_id=1,
        )
        db.session.add(self.dataset)
        db.session.commit()

    @patch("app.tasks.io_helpers.convert_bed_to_bedpe")
    @patch("app.tasks.io_helpers.clean_bed")
    @patch("app.pipeline_steps._set_task_progress")
    @patch("app.pipeline_steps.bed_preprocess_pipeline_step")
    def test_helper_calls_dispatched_correctly(
        self,
        mock_bed_pipeline_step,
        mock_set_progress,
        mock_clean_bed,
        mock_convert_bed,
    ):
        """Tests whether the functions that execute the different pipeline steps are called
        correctly."""
        # launch task
        pipeline_bed(1)
        # check whether dataset file_path is now sorted file_path
        self.assertEqual(self.dataset.file_path, "/test/path/test3_cleaned.bed")
        # check whether sort_bed was called correctly
        mock_clean_bed.assert_called_with(
            *[
                "/test/path/test3.bed",
                "/test/path/test3_cleaned.bed",
            ]
        )
        # check whether convert_bed_to_bedpe and bed_pipeline_step was called correctly
        for window in self.app.config["PREPROCESSING_MAP"].keys():
            # target_file = "/test/path/test3_sorted.bed" + f".{window}" + ".bedpe"
            # mock_convert_bed.assert_any_call(
            #    *["/test/path/test3_sorted.bed", target_file, window]
            # )
            mock_bed_pipeline_step.assert_any_call(*[1, window])
        # check whether set_progress was called with 100 last
        mock_set_progress.assert_called_with(100)

    @patch("app.tasks.io_helpers.convert_bed_to_bedpe")
    def test_bed_preprocess_pipeline_step(self, mock_convert_bed):
        """Test whether components of bed_preprocess_pipline_step are called correctly."""
        # call function
        window = 400000
        bed_preprocess_pipeline_step(1, 400000)
        # check whehter convert bed to bedpe is called correctly
        target_file = "/test/path/test3.bed" + f".{window}" + ".bedpe"
        mock_convert_bed.assert_called_with(
            *["/test/path/test3.bed", target_file, window]
        )


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
