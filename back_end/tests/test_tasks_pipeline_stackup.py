import sys
import unittest
from unittest.mock import patch
from unittest.mock import MagicMock, PropertyMock
import pandas as pd
from pandas.testing import assert_series_equal
from test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
sys.path.append("./")
from app import db
from app.models import Dataset, Intervals
from app.tasks import pipeline_stackup
from app.pipeline_steps import perform_pileup


class TestPipelineStackup(LoginTestCase, TempDirTestCase):
    """Tests whether pipelin_stackup task calls
    the pipeline steps correctly"""

    def setUp(self):
        """Add test dataset"""
        # call setUp of LoginTestCase to initialize app
        super(TestPipelineStackup, self).setUp()
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
            higlass_uuid="fdsa8765",
            filetype="bigwig",
            processing_state="finished",
            user_id=1,
        )
        # add intervals
        self.intervals1 = Intervals(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            higlass_uuid="testHiglass1",
            windowsize=200000,
        )
        self.intervals2 = Intervals(
            name="testRegion2",
            dataset_id=1,
            file_path="test_path_2.bedd2db",
            higlass_uuid="testHiglass2",
            windowsize=200000,
        )
        db.session.add(self.dataset)
        db.session.add(self.intervals1)
        db.session.add(self.intervals2)
        db.session.commit()

    @patch("app.pipeline_steps._set_task_progress")
    @patch("app.pipeline_steps.perform_stackup")
    def test_pipeline_stackup_calls_steps_correctly(
        self, mock_perform_stackup, mock_set_progress
    ):
        """Tests whether the functions that execute the different pipeline steps are called
        correctly."""
        # launch task
        binsizes = [10000, 20000, 30000]
        dataset_id = 1
        intervals_id = [1, 2]
        intervals_objects = [self.intervals1, self.intervals2]
        pipeline_stackup(dataset_id, binsizes, intervals_id)
        # compare expected call arguments with actual call arguments
        for binsize in binsizes:
                for intervals in intervals_objects:
                    # check whether the current combination is in call args list
                    expected_call_args = [self.dataset, intervals, binsize]
                    mock_perform_stackup.assert_any_call(*expected_call_args)
        # check whether number of calls was as expected
        self.assertEqual(
            mock_perform_stackup.call_count, len(binsizes) * len(intervals_objects)
        )
        # check whether last call to set task progress was 100
        mock_set_progress.assert_called_with(100)


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
            higlass_uuid="fdsa8765",
            filetype="bigwig",
            processing_state="finished",
            user_id=1,
        )
        self.dataset2 = Dataset(
            dataset_name="test4",
            file_path="/test/path/test4.bw",
            higlass_uuid="fdsa87615",
            filetype="bigwig",
            processing_state="finished",
            user_id=1,
        )
        # add intervals
        self.intervals1 = Intervals(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            higlass_uuid="testHiglass1",
            windowsize=200000,
        )
        self.intervals2 = Intervals(
            name="testRegion2",
            dataset_id=1,
            file_path="test_path_2.bedd2db",
            higlass_uuid="testHiglass2",
            windowsize=300000,
        )
        db.session.add(self.dataset)
        db.session.add(self.dataset2)
        db.session.add(self.intervals1)
        db.session.add(self.intervals2)
        db.session.commit()


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
