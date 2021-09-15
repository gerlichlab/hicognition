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
from app.models import Dataset, Intervals, Assembly, Task
from app.tasks import pipeline_pileup
from app.pipeline_steps import perform_pileup


class TestPipelinePileup(LoginTestCase, TempDirTestCase):
    """Tests whether pipelin_pileup task calls
    the pipeline steps correctly"""

    def setUp(self):
        """Add test dataset"""
        # call setUp of LoginTestCase to initialize app
        super(TestPipelinePileup, self).setUp()
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
        self.bedfile = Dataset(
            id=1,
            filetype="bedfile",
            user_id=1,
            assembly=1
        )
        self.coolerfile = Dataset(
            id=2,
            filetype="cooler",
            user_id=1,
            assembly=1
        )
        # add intervals
        self.intervals1 = Intervals(
            id=1,
            name="testRegion1",
            dataset_id=1,
            windowsize=200000,
        )
        self.intervals2 = Intervals(
            id=2,
            name="testRegion2",
            dataset_id=1,
            windowsize=200000,
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

    @staticmethod
    def get_call_args_without_index(mock, remove_index):
        """extracts call args from magic mock object and removes
        object at index"""
        call_args = []
        for call in mock.call_args_list:
            current_call_list = []
            for index in range(len(call[0])):
                if index == remove_index:
                    # remove chromosome arms dataframe
                    continue
                current_call_list.append(call[0][index])
            call_args.append(current_call_list)
        return call_args

    @patch("app.pipeline_steps._set_task_progress")
    @patch("app.pipeline_steps.perform_pileup")
    def test_pipeline_pileup_calls_steps_correctly(
        self, mock_perform_pileup, mock_set_progress
    ):
        """Tests whether the functions that execute the different pipeline steps are called
        correctly."""
        # add datasets
        db.session.add_all([self.coolerfile, self.bedfile, self.intervals1, self.intervals2])
        db.session.commit()
        # launch task
        binsize = 10000
        dataset_id = 2
        intervals_id = 2
        pileup_types = ["ICCF", "Obs/Exp"]
        pipeline_pileup(dataset_id, intervals_id, binsize)
        # construct call arguments, pd.dataframe breaks magicmocks interval methods
        call_args = self.get_call_args_without_index(mock_perform_pileup, 3)
        # compare expected call arguments with actual call arguments
        for pileup_type in pileup_types:
            # check whether the current combination is in call args list
            expected_call_args = [dataset_id, intervals_id, binsize, pileup_type]
            self.assertTrue(expected_call_args in call_args)
        # check whether number of calls was as expected
        self.assertEqual(len(call_args), len(pileup_types))
        # check whether last call to set task progress was 100
        mock_set_progress.assert_called_with(100)

    @patch("app.pipeline_steps.pd.read_csv")
    @patch("app.pipeline_steps._set_task_progress")
    @patch("app.pipeline_steps.perform_pileup")
    def test_dataset_state_not_changed_if_not_last(self, mock_pileup, mock_set_progress, mock_read_csv):
        """tests whether dataset state is left unchanged if it is not the last task for
        this dataset/intervals combination."""
        # set up database
        self.bedfile.processing_features = [self.coolerfile]
        db.session.add_all([self.bedfile, self.coolerfile, self.intervals1, self.unfinished_task1])
        # call pipeline
        pipeline_pileup(2, 1, 10000)
        # check whether processing has finished
        self.assertEqual(self.bedfile.processing_features, [self.coolerfile])

    @patch("app.pipeline_steps.pd.read_csv")
    @patch("app.pipeline_steps._set_task_progress")
    @patch("app.pipeline_steps.perform_pileup")
    def test_dataset_set_finished_if_last(self, mock_pileup, mock_set_progress, mock_read_csv):
        """tests whether dataset is set finished correctly if it is the last task for
        this dataset/intervals combination."""
        # set up database
        self.bedfile.processing_features = [self.coolerfile]
        db.session.add_all([self.bedfile, self.coolerfile, self.intervals1, self.finished_task1])
        # call pipeline
        pipeline_pileup(2, 1, 10000)
        # check whether processing has finished
        self.assertEqual(self.bedfile.processing_features, [])

    @patch("app.pipeline_steps.log.error")
    @patch("app.pipeline_steps.pd.read_csv")
    @patch("app.pipeline_steps._set_task_progress")
    @patch("app.pipeline_steps.perform_pileup")
    def test_dataset_set_failed_if_failed(self, mock_pileup, mock_set_progress, mock_read_csv, mock_log):
        """tests whether dataset is set as faild if problem arises."""
        # set up exception raising
        mock_pileup.side_effect = ValueError("Test")
        # set up database
        self.bedfile.processing_features = [self.coolerfile]
        db.session.add_all([self.bedfile, self.coolerfile, self.intervals1, self.unfinished_task1])
        # call pipeline
        pipeline_pileup(2, 1, 10000)
        # check whether processing has finished
        self.assertEqual(self.bedfile.failed_features, [self.coolerfile])
        self.assertEqual(self.bedfile.processing_features, [])
        assert mock_log.called


class TestPerformPileup(LoginTestCase, TempDirTestCase):
    def setUp(self):
        """Add test dataset"""
        # call setUp of LoginTestCase to initialize app
        super(TestPerformPileup, self).setUp()
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
        self.dataset = Dataset(
            dataset_name="test3",
            file_path="/test/path/test3.mcool",
            filetype="cooler",
            processing_state="finished",
            user_id=1,
            assembly=1
        )
        self.dataset2 = Dataset(
            dataset_name="test4",
            file_path="/test/path/test4.mcool",
            filetype="cooler",
            processing_state="finished",
            user_id=1,
            assembly=1
        )
        # add intervals
        self.intervals1 = Intervals(
            name="testRegion1",
            dataset_id=1,
            windowsize=200000,
        )
        self.intervals2 = Intervals(
            name="testRegion2",
            dataset_id=1,
            windowsize=300000,
        )
        db.session.add(self.dataset)
        db.session.add(self.dataset2)
        db.session.add(self.intervals1)
        db.session.add(self.intervals2)
        db.session.commit()

    @patch("app.pipeline_steps.add_pileup_db")
    @patch("app.pipeline_steps.HT.do_pileup_iccf")
    @patch("app.pipeline_steps.HT.do_pileup_obs_exp")
    @patch("app.pipeline_steps.HT.get_expected")
    @patch("app.pipeline_steps.HT.assign_regions")
    @patch("app.pipeline_steps.cooler.Cooler")
    @patch("app.pipeline_steps.pd.read_csv")
    def test_assign_regions_start_end_regions_handled_correctly(
        self,
        mock_read_csv,
        mock_Cooler,
        mock_assign_regions,
        mock_get_expected,
        mock_pileup_obs_exp,
        mock_pileup_iccf,
        mock_add_db,
    ):
        """Tests whether regions that are defined as chrom, start, end are handled correctly."""
        test_df_interval = pd.DataFrame(
            {0: ["chr1", "chr1"], 1: [0, 1000], 2: [1000, 2000]}
        )
        mock_read_csv.return_value = test_df_interval
        # dispatch call
        dataset_id = 1
        intervals_id = 1
        arms = pd.read_csv(self.app.config["CHROM_ARMS"])
        perform_pileup(dataset_id, intervals_id, 10000, arms, "ICCF")
        # check whether assign regions was called with correct arguments
        expected_df = pd.DataFrame({"chrom": ["chr1", "chr1"], "pos": [500, 1500]})
        window_size, binsize, chrom_called, pos_called = mock_assign_regions.call_args[
            0
        ][:4]
        self.assertEqual(window_size, 200000)
        self.assertEqual(binsize, 10000)
        assert_series_equal(chrom_called, expected_df["chrom"])
        assert_series_equal(pos_called, expected_df["pos"])

    @patch("app.pipeline_steps.add_pileup_db")
    @patch("app.pipeline_steps.HT.do_pileup_iccf")
    @patch("app.pipeline_steps.HT.do_pileup_obs_exp")
    @patch("app.pipeline_steps.HT.get_expected")
    @patch("app.pipeline_steps.HT.assign_regions")
    @patch("app.pipeline_steps.cooler.Cooler")
    @patch("app.pipeline_steps.pd.read_csv")
    def test_assign_regions_pos_regions_handled_correctly(
        self,
        mock_read_csv,
        mock_Cooler,
        mock_assign_regions,
        mock_get_expected,
        mock_pileup_obs_exp,
        mock_pileup_iccf,
        mock_add_db,
    ):
        """Tests whether regions that are defined as chrom, pos are handled correctly."""
        test_df_interval = pd.DataFrame({0: ["chr1", "chr1"], 1: [500, 1500]})
        mock_read_csv.return_value = test_df_interval
        # dispatch call
        dataset_id = 1
        intervals_id = 1
        arms = pd.read_csv(self.app.config["CHROM_ARMS"])
        perform_pileup(dataset_id, intervals_id, 10000, arms, "ICCF")
        # check whether assign regions was called with correct arguments
        expected_df = pd.DataFrame({"chrom": ["chr1", "chr1"], "pos": [500, 1500]})
        window_size, binsize, chrom_called, pos_called = mock_assign_regions.call_args[
            0
        ][:4]
        self.assertEqual(window_size, 200000)
        self.assertEqual(binsize, 10000)
        assert_series_equal(chrom_called, expected_df["chrom"])
        assert_series_equal(pos_called, expected_df["pos"])

    @patch("app.pipeline_steps.add_pileup_db")
    @patch("app.pipeline_steps.HT.do_pileup_iccf")
    @patch("app.pipeline_steps.HT.do_pileup_obs_exp")
    @patch("app.pipeline_steps.HT.get_expected")
    @patch("app.pipeline_steps.HT.assign_regions")
    @patch("app.pipeline_steps.cooler.Cooler")
    @patch("app.pipeline_steps.pd.read_csv")
    def test_correct_cooler_used(
        self,
        mock_read_csv,
        mock_Cooler,
        mock_assign_regions,
        mock_get_expected,
        mock_pileup_obs_exp,
        mock_pileup_iccf,
        mock_add_db,
    ):
        """Tests whether correct cooler is used for pileup."""
        test_df_interval = pd.DataFrame({0: ["chr1", "chr1"], 1: [500, 1500]})
        mock_read_csv.return_value = test_df_interval
        # dispatch call
        dataset_id = 1
        intervals_id = 1
        arms = pd.read_csv(self.app.config["CHROM_ARMS"])
        perform_pileup(dataset_id, intervals_id, 10000, arms, "ICCF")
        # check whether corrrect cooler file was called with correct binsize
        expected_call = self.dataset.file_path + "::/resolutions/10000"
        mock_Cooler.assert_called_with(expected_call)

    @patch("app.pipeline_steps.add_pileup_db")
    @patch("app.pipeline_steps.HT.do_pileup_iccf")
    @patch("app.pipeline_steps.HT.do_pileup_obs_exp")
    @patch("app.pipeline_steps.HT.get_expected")
    @patch("app.pipeline_steps.HT.assign_regions")
    @patch("app.pipeline_steps.cooler.Cooler")
    @patch("app.pipeline_steps.pd.read_csv")
    def test_correct_functions_called_whenObsExp(
        self,
        mock_read_csv,
        mock_Cooler,
        mock_assign_regions,
        mock_get_expected,
        mock_pileup_obs_exp,
        mock_pileup_iccf,
        mock_add_db,
    ):
        """Tests whether correct cooler is used for pileup."""
        test_df_interval = pd.DataFrame({0: ["chr1", "chr1"], 1: [500, 1500]})
        mock_read_csv.return_value = test_df_interval
        mock_Cooler.return_value = "mock_cooler"
        returned_regions = MagicMock()
        mock_assign_regions.return_value = returned_regions
        mock_get_expected.return_value = "expected"
        # dispatch call
        dataset_id = 1
        intervals_id = 1
        arms = pd.read_csv(self.app.config["CHROM_ARMS"])
        perform_pileup(dataset_id, intervals_id, 10000, arms, "Obs/Exp")
        # check whether get_expected was called
        mock_get_expected.assert_called()
        expected_pileup_call = ["mock_cooler", "expected", returned_regions.dropna()]
        mock_pileup_obs_exp.assert_called_with(*expected_pileup_call, proc=1)
        # check whether iccf pileup is not called
        mock_pileup_iccf.assert_not_called()

    @patch("app.pipeline_steps.add_pileup_db")
    @patch("app.pipeline_steps.HT.do_pileup_iccf")
    @patch("app.pipeline_steps.HT.do_pileup_obs_exp")
    @patch("app.pipeline_steps.HT.get_expected")
    @patch("app.pipeline_steps.HT.assign_regions")
    @patch("app.pipeline_steps.cooler.Cooler")
    @patch("app.pipeline_steps.pd.read_csv")
    def test_correct_functions_called_whenICCF(
        self,
        mock_read_csv,
        mock_Cooler,
        mock_assign_regions,
        mock_get_expected,
        mock_pileup_obs_exp,
        mock_pileup_iccf,
        mock_add_db,
    ):
        """Tests whether correct cooler is used for pileup."""
        test_df_interval = pd.DataFrame({0: ["chr1", "chr1"], 1: [500, 1500]})
        mock_read_csv.return_value = test_df_interval
        mock_Cooler.return_value = "mock_cooler"
        returned_regions = MagicMock()
        mock_assign_regions.return_value = returned_regions
        # dispatch call
        dataset_id = 1
        intervals_id = 1
        arms = pd.read_csv(self.app.config["CHROM_ARMS"])
        perform_pileup(dataset_id, intervals_id, 10000, arms, "ICCF")
        # check whether get_expected was called
        expected_pileup_call = ["mock_cooler", returned_regions.dropna()]
        mock_pileup_iccf.assert_called_with(*expected_pileup_call, proc=1)
        # check whether iccf pileup is not called
        mock_get_expected.assert_not_called()
        mock_pileup_obs_exp.assert_not_called()

    @patch("app.pipeline_steps.uuid.uuid4")
    @patch("app.pipeline_steps.add_pileup_db")
    @patch("app.pipeline_steps.HT.do_pileup_iccf")
    @patch("app.pipeline_steps.HT.do_pileup_obs_exp")
    @patch("app.pipeline_steps.HT.get_expected")
    @patch("app.pipeline_steps.HT.assign_regions")
    @patch("app.pipeline_steps.cooler.Cooler")
    @patch("app.pipeline_steps.pd.read_csv")
    def test_adding_to_db_called_correctly(
        self,
        mock_read_csv,
        mock_Cooler,
        mock_assign_regions,
        mock_get_expected,
        mock_pileup_obs_exp,
        mock_pileup_iccf,
        mock_add_db,
        mock_uuid,
    ):
        """Tests whether conversion function as df for java script is called correctly"""
        test_df_interval = pd.DataFrame({0: ["chr1", "chr1"], 1: [500, 1500]})
        mock_read_csv.return_value = test_df_interval
        mock_pileup_iccf.return_value = "testCooler"
        # hack in return value of uuid4().hex to be asdf
        uuid4 = MagicMock()
        type(uuid4).hex = PropertyMock(return_value="asdf")
        mock_uuid.return_value = uuid4
        # construct call args
        dataset_id = 1
        intervals_id = 1
        arms = pd.read_csv(self.app.config["CHROM_ARMS"])
        perform_pileup(dataset_id, intervals_id, 10000, arms, "ICCF")
        # check whether get_expected was called
        mock_add_db.assert_called_with(
            self.app.config["UPLOAD_DIR"] + "/asdf.npy",
            10000,
            self.intervals1.id,
            self.dataset.id,
            "ICCF",
        )


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
