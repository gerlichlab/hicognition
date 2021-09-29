import sys
import unittest
from unittest.mock import patch
from unittest.mock import MagicMock, PropertyMock
import pandas as pd
import numpy as np
from pandas.testing import assert_series_equal
from test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
sys.path.append("./")
from app import db
from app.models import Dataset, Intervals, Assembly, Task
from app.tasks import pipeline_pileup
from app.pipeline_steps import pileup_pipeline_step
from app.pipeline_worker_functions import _do_pileup_fixed_size, _do_pileup_variable_size
from app.api.helpers import get_optimal_binsize


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
        self.bedfile = Dataset(id=1, filetype="bedfile", user_id=1, assembly=1)
        self.coolerfile = Dataset(id=2, filetype="cooler", user_id=1, assembly=1)
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
            id="test1", dataset_id=2, intervals_id=1, complete=True
        )
        self.unfinished_task1 = Task(
            id="test1", dataset_id=2, intervals_id=1, complete=False
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

    @patch("app.pipeline_steps.set_task_progress")
    @patch("app.pipeline_steps.pileup_pipeline_step")
    def test_pipeline_pileup_calls_steps_correctly(
        self, mock_pileup_pipeline_step, mock_set_progress
    ):
        """Tests whether the functions that execute the different pipeline steps are called
        correctly."""
        # add datasets
        db.session.add_all(
            [self.coolerfile, self.bedfile, self.intervals1, self.intervals2]
        )
        db.session.commit()
        # launch task
        binsize = 10000
        dataset_id = 2
        intervals_id = 2
        pileup_types = ["ICCF", "Obs/Exp"]
        pipeline_pileup(dataset_id, intervals_id, binsize)
        # construct call arguments, pd.dataframe breaks magicmocks interval methods
        call_args = self.get_call_args_without_index(mock_pileup_pipeline_step, 3)
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
    @patch("app.pipeline_steps.set_task_progress")
    @patch("app.pipeline_steps.pileup_pipeline_step")
    def test_dataset_state_not_changed_if_not_last(
        self, mock_pileup, mock_set_progress, mock_read_csv
    ):
        """tests whether dataset state is left unchanged if it is not the last task for
        this dataset/intervals combination."""
        # set up database
        self.bedfile.processing_features = [self.coolerfile]
        db.session.add_all(
            [self.bedfile, self.coolerfile, self.intervals1, self.unfinished_task1]
        )
        # call pipeline
        pipeline_pileup(2, 1, 10000)
        # check whether processing has finished
        self.assertEqual(self.bedfile.processing_features, [self.coolerfile])

    @patch("app.pipeline_steps.pd.read_csv")
    @patch("app.pipeline_steps.set_task_progress")
    @patch("app.pipeline_steps.pileup_pipeline_step")
    def test_dataset_set_finished_if_last(
        self, mock_pileup, mock_set_progress, mock_read_csv
    ):
        """tests whether dataset is set finished correctly if it is the last task for
        this dataset/intervals combination."""
        # set up database
        self.bedfile.processing_features = [self.coolerfile]
        db.session.add_all(
            [self.bedfile, self.coolerfile, self.intervals1, self.finished_task1]
        )
        # call pipeline
        pipeline_pileup(2, 1, 10000)
        # check whether processing has finished
        self.assertEqual(self.bedfile.processing_features, [])

    @patch("app.pipeline_steps.log.error")
    @patch("app.pipeline_steps.pd.read_csv")
    @patch("app.pipeline_steps.set_task_progress")
    @patch("app.pipeline_steps.pileup_pipeline_step")
    def test_dataset_set_failed_if_failed(
        self, mock_pileup, mock_set_progress, mock_read_csv, mock_log
    ):
        """tests whether dataset is set as faild if problem arises."""
        # set up exception raising
        mock_pileup.side_effect = ValueError("Test")
        # set up database
        self.bedfile.processing_features = [self.coolerfile]
        db.session.add_all(
            [self.bedfile, self.coolerfile, self.intervals1, self.unfinished_task1]
        )
        # call pipeline
        pipeline_pileup(2, 1, 10000)
        # check whether processing has finished
        self.assertEqual(self.bedfile.failed_features, [self.coolerfile])
        self.assertEqual(self.bedfile.processing_features, [])
        assert mock_log.called


class TestPileupPipelineStep(LoginTestCase, TempDirTestCase):
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
        # add dataset
        self.dataset = Dataset(
            dataset_name="test3",
            file_path="/test/path/test3.mcool",
            filetype="cooler",
            processing_state="finished",
            user_id=1,
            assembly=1,
        )
        self.dataset2 = Dataset(
            dataset_name="test4",
            file_path="/test/path/test4.mcool",
            filetype="cooler",
            processing_state="finished",
            user_id=1,
            assembly=1,
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
        self.intervals3 = Intervals(
            name="testRegion2",
            dataset_id=1,
            windowsize=None,
        )
        db.session.add(self.dataset)
        db.session.add(self.dataset2)
        db.session.add(self.intervals1)
        db.session.add(self.intervals2)
        db.session.add(self.intervals3)
        db.session.commit()

    @patch("app.pipeline_steps.worker_funcs._do_pileup_fixed_size")
    @patch("app.pipeline_steps.worker_funcs._do_pileup_variable_size")
    def test_correct_pileup_worker_function_used_point_feature(
        self,
        mock_pileup_variable_size,
        mock_pileup_fixed_size,
    ):
        """Tests whether correct worker function for pileup is used
        when intervals has fixed windowsizes"""
        # dispatch call
        dataset_id = 1
        intervals_id = 1
        arms = pd.read_csv(self.app.config["CHROM_ARMS"])
        pileup_pipeline_step(dataset_id, intervals_id, 10000, arms, "ICCF")
        # check whether pileup with fixed size was called and with variable size was not called
        mock_pileup_fixed_size.assert_called_once()
        mock_pileup_variable_size.assert_not_called()

    @patch("app.pipeline_steps.worker_funcs._do_pileup_fixed_size")
    @patch("app.pipeline_steps.worker_funcs._do_pileup_variable_size")
    def test_correct_pileup_worker_function_used_interval_feature(
        self,
        mock_pileup_variable_size,
        mock_pileup_fixed_size,
    ):
        """Tests whether correct worker function for pileup is used
        when intervals has variable windowsizes"""
        # dispatch call
        dataset_id = 1
        intervals_id = 3
        arms = pd.read_csv(self.app.config["CHROM_ARMS"])
        pileup_pipeline_step(dataset_id, intervals_id, 10000, arms, "ICCF")
        # check whether pileup with fixed size was called and with variable size was not called
        mock_pileup_variable_size.assert_called_once()
        mock_pileup_fixed_size.assert_not_called()

    @patch("app.pipeline_steps.uuid.uuid4")
    @patch("app.pipeline_steps.worker_funcs._add_pileup_db")
    @patch("app.pipeline_steps.worker_funcs._do_pileup_fixed_size")
    @patch("app.pipeline_steps.worker_funcs._do_pileup_variable_size")
    def test_adding_to_db_called_correctly(
        self,
        mock_pileup_variable_size,
        mock_pileup_fixed_size,
        mock_add_db,
        mock_uuid,
    ):
        """Tests whether function to add result to database is called correctly."""
        # hack in return value of uuid4().hex to be asdf
        uuid4 = MagicMock()
        type(uuid4).hex = PropertyMock(return_value="asdf")
        mock_uuid.return_value = uuid4
        # construct call args
        dataset_id = 1
        intervals_id = 1
        arms = pd.read_csv(self.app.config["CHROM_ARMS"])
        pileup_pipeline_step(dataset_id, intervals_id, 10000, arms, "ICCF")
        # check whether get_expected was called
        mock_add_db.assert_called_with(
            self.app.config["UPLOAD_DIR"] + "/asdf.npy",
            10000,
            self.intervals1.id,
            self.dataset.id,
            "ICCF",
        )


class TestPileupWorkerFunctionsFixedSize(LoginTestCase, TempDirTestCase):
    """Test pileup worker functions for fixed sized intervals."""

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
        # add dataset
        self.cooler = Dataset(
            dataset_name="test3",
            file_path="/test/path/test3.mcool",
            filetype="cooler",
            processing_state="finished",
            user_id=1,
            assembly=1,
        )
        db.session.add(self.cooler)
        db.session.commit()


    @patch("app.pipeline_worker_functions.HT.do_pileup_iccf")
    @patch("app.pipeline_worker_functions.HT.do_pileup_obs_exp")
    @patch("app.pipeline_worker_functions.HT.get_expected")
    @patch("app.pipeline_worker_functions.HT.assign_regions")
    @patch("app.pipeline_worker_functions.cooler.Cooler")
    @patch("app.pipeline_worker_functions.pd.read_csv")
    def test_correct_functions_called_ObsExp(
        self,
        mock_read_csv,
        mock_Cooler,
        mock_assign_regions,
        mock_get_expected,
        mock_pileup_obs_exp,
        mock_pileup_iccf,
    ):
        """Tests whether correct pileup function is called when obs/exp pileup is dispatched"""
        test_df_interval = pd.DataFrame(
            {0: ["chr1", "chr1"], 1: [0, 1000], 2: [1000, 2000]}
        )
        mock_read_csv.return_value = test_df_interval
        mock_Cooler.return_value = "mock_cooler"
        returned_regions = MagicMock()
        mock_assign_regions.return_value = returned_regions
        mock_get_expected.return_value = "expected"
        # dispatch call
        arms = pd.read_csv(self.app.config["CHROM_ARMS"])
        _do_pileup_fixed_size(self.cooler, 100000, 10000, "testpath", arms, "Obs/Exp")
        # check whether get_expected was called
        mock_get_expected.assert_called()
        expected_pileup_call = ["mock_cooler", "expected", returned_regions.dropna()]
        mock_pileup_obs_exp.assert_called_with(*expected_pileup_call, proc=1)
        # check whether iccf pileup is not called
        mock_pileup_iccf.assert_not_called()

    @patch("app.pipeline_worker_functions.HT.do_pileup_iccf")
    @patch("app.pipeline_worker_functions.HT.do_pileup_obs_exp")
    @patch("app.pipeline_worker_functions.HT.get_expected")
    @patch("app.pipeline_worker_functions.HT.assign_regions")
    @patch("app.pipeline_worker_functions.cooler.Cooler")
    @patch("app.pipeline_worker_functions.pd.read_csv")
    def test_correct_functions_called_ICCF(
        self,
        mock_read_csv,
        mock_Cooler,
        mock_assign_regions,
        mock_get_expected,
        mock_pileup_obs_exp,
        mock_pileup_iccf,
    ):
        """Tests whether correct pileup function is called when iccf pileup is dispatched"""
        test_df_interval = pd.DataFrame(
            {0: ["chr1", "chr1"], 1: [0, 1000], 2: [1000, 2000]}
        )
        mock_read_csv.return_value = test_df_interval
        mock_Cooler.return_value = "mock_cooler"
        returned_regions = MagicMock()
        mock_assign_regions.return_value = returned_regions
        mock_get_expected.return_value = "expected"
        # dispatch call
        arms = pd.read_csv(self.app.config["CHROM_ARMS"])
        _do_pileup_fixed_size(self.cooler, 100000, 10000, "testpath", arms, "ICCF")
        # check whether get_expected was called
        mock_get_expected.assert_not_called()
        expected_pileup_call = ["mock_cooler", returned_regions.dropna()]
        mock_pileup_iccf.assert_called_with(*expected_pileup_call, proc=1)
        # check whether iccf pileup is not called
        mock_pileup_obs_exp.assert_not_called()


class TestPileupWorkerFunctionsVariableSize(LoginTestCase, TempDirTestCase):
    """Test pileup worker functions for variable sized intervals"""

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
        # add dataset
        self.cooler = Dataset(
            dataset_name="test3",
            file_path="/test/path/test3.mcool",
            filetype="cooler",
            processing_state="finished",
            user_id=1,
            assembly=1,
        )
        db.session.add(self.cooler)
        db.session.commit()

    @patch("app.pipeline_worker_functions.np")
    @patch("app.pipeline_worker_functions.HT.extract_windows_different_sizes_iccf")
    @patch("app.pipeline_worker_functions.HT.extract_windows_different_sizes_obs_exp")
    @patch("app.pipeline_worker_functions.HT.get_expected")
    @patch("app.pipeline_worker_functions.cooler.Cooler")
    @patch("app.pipeline_worker_functions.pd.read_csv")
    def test_correct_pileup_function_called_ObsExp(
        self,
        mock_read_csv,
        mock_Cooler,
        mock_get_expected,
        mock_pileup_obs_exp,
        mock_pileup_iccf,
        mock_np
    ):
        """Tests whether correct pileup function is called when obs/exp pileup is dispatched"""
        test_df_interval = pd.DataFrame(
            {0: ["chr1", "chr1"], 1: [0, 1000], 2: [100000, 200000]}
        )
        mock_read_csv.return_value = test_df_interval
        mock_Cooler.return_value = "mock_cooler"
        mock_get_expected.return_value = "expected"
        # dispatch call
        arms = pd.read_csv(self.app.config["CHROM_ARMS"])
        _do_pileup_variable_size(self.cooler, 5, "testpath", arms, "Obs/Exp")
        # check whether get_expected was called
        mock_get_expected.assert_called()
        mock_pileup_obs_exp.assert_called()
        # check whether iccf pileup is not called
        mock_pileup_iccf.assert_not_called()

    @patch("app.pipeline_worker_functions.np")
    @patch("app.pipeline_worker_functions.HT.extract_windows_different_sizes_iccf")
    @patch("app.pipeline_worker_functions.HT.extract_windows_different_sizes_obs_exp")
    @patch("app.pipeline_worker_functions.HT.get_expected")
    @patch("app.pipeline_worker_functions.cooler.Cooler")
    @patch("app.pipeline_worker_functions.pd.read_csv")
    def test_correct_pileup_function_called_ICCF(
        self,
        mock_read_csv,
        mock_Cooler,
        mock_get_expected,
        mock_pileup_obs_exp,
        mock_pileup_iccf,
        mock_np
    ):
        """Tests whether correct pileup function is called when obs/exp pileup is dispatched"""
        test_df_interval = pd.DataFrame(
            {0: ["chr1", "chr1"], 1: [0, 1000], 2: [100000, 200000]}
        )
        mock_read_csv.return_value = test_df_interval
        mock_Cooler.return_value = "mock_cooler"
        mock_get_expected.return_value = "expected"
        # dispatch call
        arms = pd.read_csv(self.app.config["CHROM_ARMS"])
        _do_pileup_variable_size(self.cooler, 5, "testpath", arms, "ICCF")
        # check whether get_expected was called
        mock_get_expected.assert_not_called()
        mock_pileup_iccf.assert_called()
        # check whether iccf pileup is not called
        mock_pileup_obs_exp.assert_not_called()


    @patch("app.pipeline_worker_functions.pd.read_csv")
    def test_empty_array_returned_if_binsize_none(
        self,
        mock_read_csv
    ):
        """Tests an empty array is returned when optimal binsize is none"""
        test_df_interval = pd.DataFrame(
            {0: ["chr1", "chr1"], 1: [0, 0], 2: [100, 200]}
        )
        mock_read_csv.return_value = test_df_interval
        # dispatch call
        result = _do_pileup_variable_size(self.cooler, 5, "testpath", "testarms", "ICCF")
        self.assertTrue(np.all(np.isnan(result)))


class TestGetOptimalBinsize(unittest.TestCase):
    """Tests get_optimal_binsize helper function"""

    def test_none_if_regions_too_small(self):
        """tests if none is returned if regions are too small."""
        regions = pd.DataFrame({"chrom": ["chr1"], "start": [0], "end": [10]})
        self.assertEqual(get_optimal_binsize(regions, 100), None)

    def test_none_if_regions_too_large(self):
        """tests if none is returned if regions too large"""
        regions = pd.DataFrame({"chrom": ["chr1"], "start": [0], "end": [10 ** 9]})
        self.assertEqual(get_optimal_binsize(regions, 100), None)

    def test_correct_binsize_small_size(self):
        """tests correct handling of small regions."""
        regions = pd.DataFrame({"chrom": ["chr1"], "start": [0], "end": [10000]})
        self.assertEqual(get_optimal_binsize(regions, 100), 1000)

    def test_correct_binsize_moderate_size(self):
        """tests correct handling of moderately sized regions."""
        regions = pd.DataFrame({"chrom": ["chr1"], "start": [0], "end": [500001]})
        self.assertEqual(get_optimal_binsize(regions, 100), 5000)

    def test_correct_binsize_large_size(self):
        """tests correct handling of large regions."""
        regions = pd.DataFrame({"chrom": ["chr1"], "start": [0], "end": [1000001]})
        self.assertEqual(get_optimal_binsize(regions, 100), 10000)

    def test_correct_binsize_rare_large_size(self):
        """tests correct handling of small regions with rare lare regions"""
        regions = pd.DataFrame(
            {
                "chrom": ["chr1"] * 100,
                "start": [0] * 100,
                "end": [10000] * 99 + [1000001],
            }
        )
        self.assertEqual(get_optimal_binsize(regions, 100), 1000)

    def test_correct_binsize_tads(self):
        """tests correct handling of small regions with rare lare regions"""
        regions = pd.read_csv(
            "tests/testfiles/G2_tads_w_size.bed", sep="\t", header=None
        ).rename(columns={0: "chrom", 1: "start", 2: "end"})
        self.assertEqual(get_optimal_binsize(regions, 100), 10000)

    def test_correct_binsize_tads_low_number_target_bins(self):
        """tests correct handling of small regions with rare lare regions"""
        regions = pd.read_csv(
            "tests/testfiles/G2_tads_w_size.bed", sep="\t", header=None
        ).rename(columns={0: "chrom", 1: "start", 2: "end"})
        self.assertEqual(get_optimal_binsize(regions, 50), 20000)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
