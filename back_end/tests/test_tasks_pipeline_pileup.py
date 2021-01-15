import sys
import unittest
from unittest.mock import patch
import pandas as pd
from test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
sys.path.append("./")
from app import db
from app.models import Dataset, Intervals
from app.tasks import pipeline_pileup


class TestPipelinePileup(LoginTestCase, TempDirTestCase):
    """Tests whether pipelin_bed task calls
    the pipeline steps correctly"""

    def setUp(self):
        """Add test dataset"""
        # call setUp of LoginTestCase to initialize app
        super(TestPipelinePileup, self).setUp()
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token_header
        token_headers = self.get_token_header(token)
        # add content-type
        token_headers["Content-Type"] = "multipart/form-data"
        # add dataset
        self.dataset = Dataset(
            dataset_name="test3",
            file_path="/test/path/test3.mcool",
            higlass_uuid="fdsa8765",
            filetype="cooler",
            processing_state="finished",
            user_id=1,
        )
        # add intervals
        self.intervals1 = Intervals(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            higlass_uuid="testHiglass1",
            windowsize=200000
        )
        self.intervals2 = Intervals(
            name="testRegion2",
            dataset_id=1,
            file_path="test_path_2.bedd2db",
            higlass_uuid="testHiglass2",
            windowsize=200000
        )
        db.session.add(self.dataset)
        db.session.add(self.intervals1)
        db.session.add(self.intervals2)
        db.session.commit()

    @patch("app.tasks._set_task_progress")
    @patch("app.tasks.perform_pileup")
    def test_pipeline_pileup_calls_steps_correctly(self, mock_perform_pileup, mock_set_progress):
        """Tests whether the functions that execute the different pipeline steps are called
        correctly."""
        # launch task
        binsizes = [10000, 20000, 30000]
        dataset_id = 1
        intervals_id = [1, 2]
        pileup_types = ["ICCF", "Obs/Exp"]
        intervals_objects = [self.intervals1, self.intervals2]
        pipeline_pileup(dataset_id, binsizes, intervals_id)
        # construct call arguments, pd.dataframe breaks magicmocks interval methods
        call_args = []
        for call in mock_perform_pileup.call_args_list:
            current_call_list = []
            for index in range(len(call[0])):
                if index == 3:
                    # remove chromosome arms dataframe
                    continue
                current_call_list.append(call[0][index])
            call_args.append(current_call_list)
        # compare expected call arguments with actual call arguments
        for binsize in binsizes:
            for pileup_type in pileup_types:
                for intervals in intervals_objects:
                    # check whether the current combination is in call args list
                    expected_call_args = [self.dataset, intervals, binsize, pileup_type]
                    self.assertTrue(expected_call_args in call_args)
        # check whether number of calls was as expected
        self.assertEqual(len(call_args), len(binsizes) * len(pileup_types) * len(intervals_objects))
        # check whether last call to set task progress was 100
        mock_set_progress.assert_called_with(100)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
