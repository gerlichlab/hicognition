import os
import sys
import unittest
from unittest.mock import patch
from unittest.mock import MagicMock, PropertyMock
import pandas as pd
from pandas.testing import assert_frame_equal
import numpy as np
from hicognition.test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
sys.path.append("./")
from app import db
from app.models import Dataset, Intervals, Assembly, Task, ObsExp
from app.tasks import pipeline_pileup
from app.pipeline_steps import pileup_pipeline_step
from app.pipeline_worker_functions import (
    _do_pileup_fixed_size,
    _do_pileup_variable_size,
)
from hicognition.utils import get_optimal_binsize


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
            id=1, name="testRegion1", dataset_id=1, windowsize=200000
        )
        self.intervals2 = Intervals(
            id=2, name="testRegion2", dataset_id=1, windowsize=200000
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
        self.intervals1 = Intervals(name="testRegion1", dataset_id=1, windowsize=200000)
        self.intervals2 = Intervals(name="testRegion2", dataset_id=1, windowsize=300000)
        self.intervals3 = Intervals(name="testRegion2", dataset_id=1, windowsize=None)
        db.session.add(self.dataset)
        db.session.add(self.dataset2)
        db.session.add(self.intervals1)
        db.session.add(self.intervals2)
        db.session.add(self.intervals3)
        db.session.commit()

    @patch("app.pipeline_steps.worker_funcs._do_pileup_fixed_size")
    @patch("app.pipeline_steps.worker_funcs._do_pileup_variable_size")
    def test_correct_pileup_worker_function_used_point_feature(
        self, mock_pileup_variable_size, mock_pileup_fixed_size
    ):
        """Tests whether correct worker function for pileup is used
        when intervals has fixed windowsizes"""
        # add return values
        mock_pileup_fixed_size.return_value = np.full((2, 2, 2), np.nan)
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
        self, mock_pileup_variable_size, mock_pileup_fixed_size
    ):
        """Tests whether correct worker function for pileup is used
        when intervals has variable windowsizes"""
        # add return values
        mock_pileup_variable_size.return_value = np.full((2, 2, 2), np.nan)
        # dispatch call
        dataset_id = 1
        intervals_id = 3
        arms = pd.read_csv(self.app.config["CHROM_ARMS"])
        pileup_pipeline_step(dataset_id, intervals_id, 10000, arms, "ICCF")
        # check whether pileup with fixed size was called and with variable size was not called
        mock_pileup_variable_size.assert_called_once()
        mock_pileup_fixed_size.assert_not_called()

    @patch("app.pipeline_steps.uuid.uuid4")
    @patch("app.pipeline_steps.worker_funcs._add_embedding_2d_to_db")
    @patch("app.pipeline_steps.worker_funcs._add_pileup_db")
    @patch("app.pipeline_steps.worker_funcs._do_pileup_fixed_size")
    @patch("app.pipeline_steps.worker_funcs._do_pileup_variable_size")
    def test_adding_to_db_called_correctly(
        self, mock_pileup_variable_size, mock_pileup_fixed_size, mock_add_pileup_db, mock_add_embedding_db, mock_uuid
    ):
        """Tests whether function to add result to database is called correctly."""
        # add return values
        mock_pileup_fixed_size.return_value = np.full((2, 2, 2), np.nan)
        # hack in return value of uuid4().hex to be asdf
        uuid4 = MagicMock()
        type(uuid4).hex = PropertyMock(return_value="asdf")
        mock_uuid.return_value = uuid4
        # construct call args
        dataset_id = 1
        intervals_id = 1
        arms = pd.read_csv(self.app.config["CHROM_ARMS"])
        pileup_pipeline_step(dataset_id, intervals_id, 10000, arms, "ICCF")
        # check whether adding to pileup db is called correctly
        mock_add_pileup_db.assert_called_with(
            self.app.config["UPLOAD_DIR"] + "/asdf.npy",
            10000,
            self.intervals1.id,
            self.dataset.id,
            "ICCF",
        )
        # check whether adding embedding to db is called correctly
        mock_add_embedding_db.assert_any_call(
            {
                "embedding": self.app.config["UPLOAD_DIR"] + "/asdf_embedding.npy",
                "cluster_ids": self.app.config["UPLOAD_DIR"] + "/asdf_cluster_ids_small.npy",
                "thumbnails": self.app.config["UPLOAD_DIR"] + "/asdf_thumbnails_small.npy",
            },
            10000,
            self.intervals1.id,
            self.dataset.id,
            "ICCF",
            "small"
        )
        mock_add_embedding_db.assert_any_call(
            {
                "embedding": self.app.config["UPLOAD_DIR"] + "/asdf_embedding.npy",
                "cluster_ids": self.app.config["UPLOAD_DIR"] + "/asdf_cluster_ids_large.npy",
                "thumbnails": self.app.config["UPLOAD_DIR"] + "/asdf_thumbnails_large.npy",
            },
            10000,
            self.intervals1.id,
            self.dataset.id,
            "ICCF",
            "large"
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
            file_path="./tests/testfiles/test.mcool",
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
        mock_get_expected.return_value = pd.DataFrame()
        # dispatch call
        arms = pd.read_csv(self.app.config["CHROM_ARMS"])
        _do_pileup_fixed_size(self.cooler, 100000, 10000, "testpath", arms, "Obs/Exp")
        # check whether get_expected was called
        mock_get_expected.assert_called()
        mock_pileup_obs_exp.assert_called()
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
        mock_pileup_iccf.assert_called_with(
            *expected_pileup_call, proc=2, collapse=True
        )
        # check whether iccf pileup is not called
        mock_pileup_obs_exp.assert_not_called()

    def test_regions_with_bad_chromosomes_filled_with_nan(self):
        """Checks whether regions with bad chromosomes are filled with nans"""
        arms = pd.read_csv(self.app.config["CHROM_ARMS"])
        with patch("app.pipeline_worker_functions.pd.read_csv") as mock_read_csv:
            test_df_interval = pd.DataFrame(
                {
                    0: ["chr1", "chrASDF", "chr1", "chrASDF"],
                    1: [60000000, 10, 50000000, 100],
                    2: [60000000, 10, 50000000, 150],
                }
            )
            mock_read_csv.return_value = test_df_interval
            # dispatch call
            result = _do_pileup_fixed_size(
                self.cooler, 10000000, 5000000, "testpath", arms, "ICCF", collapse=False
            )
        self.assertEqual(result.shape[2], 4)
        test_array_one = np.array(
            [
                [0.13717751, 0.0265284, 0.01462106, 0.009942, 0.00682112],
                [0.0265284, 0.18850834, 0.06237434, 0.0145492, 0.01485787],
                [0.01462106, 0.06237434, 0.119365, 0.04225391, 0.01654861],
                [0.009942, 0.0145492, 0.04225391, 0.12408607, 0.05381814],
                [0.00682112, 0.01485787, 0.01654861, 0.05381814, 0.14363506],
            ]
        )
        test_array_two = np.array(
            [
                [0.23130276, 0.02327701, 0.0126868, 0.00436247, 0.00401918],
                [0.02327701, 0.15173886, 0.07788348, 0.01425616, 0.01083477],
                [0.0126868, 0.07788348, 0.13717751, 0.0265284, 0.01462106],
                [0.00436247, 0.01425616, 0.0265284, 0.18850834, 0.06237434],
                [0.00401918, 0.01083477, 0.01462106, 0.06237434, 0.119365],
            ]
        )
        self.assertTrue(np.allclose(result[..., 0], test_array_one))
        self.assertTrue(np.all(np.isnan(result[..., 1])))
        self.assertTrue(np.allclose(result[..., 2], test_array_two))
        self.assertTrue(np.all(np.isnan(result[..., 3])))

    def test_cooler_w_missing_resolutions_return_nans_w_collapse(self):
        """Tests whether calling pileup on a cooler with
        a binsize that is not available returns an array of nans
        with the right shape according to windowsize and binsize"""
        arms = pd.read_csv(self.app.config["CHROM_ARMS"])
        with patch("app.pipeline_worker_functions.pd.read_csv") as mock_read_csv:
            test_df_interval = pd.DataFrame(
                {
                    0: ["chr1"],
                    1: [60000000],
                    2: [60000000],
                }
            )
            mock_read_csv.return_value = test_df_interval
            # dispatch call
            result = _do_pileup_fixed_size(
                self.cooler, 200000, 10000, "testpath", arms, "ICCF", collapse=True
            )
        self.assertEqual(result.shape, (40, 40))
        self.assertTrue(np.all(np.isnan(result)))

    def test_cooler_w_missing_resolutions_return_nans_wo_collapse(self):
        """Tests whether calling pileup on a cooler with
        a binsize that is not available returns an array of nans
        with the right shape according to windowsize and binsize"""
        arms = pd.read_csv(self.app.config["CHROM_ARMS"])
        with patch("app.pipeline_worker_functions.pd.read_csv") as mock_read_csv:
            test_df_interval = pd.DataFrame(
                {
                    0: ["chr1", "chr1"],
                    1: [60000000, 10000],
                    2: [60000000, 10000],
                }
            )
            mock_read_csv.return_value = test_df_interval
            # dispatch call
            result = _do_pileup_fixed_size(
                self.cooler, 200000, 10000, "testpath", arms, "ICCF", collapse=False
            )
        self.assertEqual(result.shape, (40, 40, 2))
        self.assertTrue(np.all(np.isnan(result)))

    @patch("app.pipeline_worker_functions.HT.get_expected")
    def test_cached_obs_exp_used(self, mock_expected):
        """Tests whether cached obs/exp dataset is used"""
        arms = pd.read_csv(self.app.config["CHROM_ARMS"])
        obs_exp = ObsExp(
            dataset_id=self.cooler.id,
            binsize=5000000,
            filepath=os.path.join("./tests/testfiles", "expected.csv"),
        )
        db.session.add(obs_exp)
        db.session.commit()
        # create mock regions
        test_df_interval = pd.DataFrame(
            {
                0: ["chr1", "chr1"],
                1: [60000000, 10000],
                2: [60000000, 10000],
            }
        )
        mock_path = os.path.join(self.app.config["UPLOAD_DIR"], "mock_regions.csv")
        test_df_interval.to_csv(mock_path, index=False, header=None, sep="\t")
        # dispatch call
        _do_pileup_fixed_size(
            self.cooler, 10000000, 5000000, mock_path, arms, "Obs/Exp", collapse=False
        )
        mock_expected.assert_not_called()

    def test_calculated_obs_exp_cached(self):
        """Tests whether cached obs/exp dataset is created if it does not exist already"""
        arms = pd.read_csv(self.app.config["CHROM_ARMS"])
        # create mock regions
        test_df_interval = pd.DataFrame(
            {
                0: ["chr1", "chr1"],
                1: [60000000, 10000],
                2: [60000000, 10000],
            }
        )
        mock_path = os.path.join(self.app.config["UPLOAD_DIR"], "mock_regions.csv")
        test_df_interval.to_csv(mock_path, index=False, header=None, sep="\t")
        # dispatch call
        _do_pileup_fixed_size(
            self.cooler, 10000000, 5000000, mock_path, arms, "Obs/Exp", collapse=False
        )
        self.assertEqual(1, len(ObsExp.query.all()))
        ds = ObsExp.query.first()
        self.assertEqual(ds.dataset_id, self.cooler.id)
        self.assertEqual(ds.binsize, 5000000)
        # load ds
        expected = pd.read_csv(os.path.join("./tests/testfiles", "expected.csv"))
        calculated = pd.read_csv(ds.filepath)
        assert_frame_equal(expected, calculated)


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
            file_path="./tests/testfiles/test.mcool",
            filetype="cooler",
            processing_state="finished",
            user_id=1,
            assembly=1,
        )
        # get arms
        self.arms = pd.read_csv(self.app.config["CHROM_ARMS"])
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
        mock_np,
    ):
        """Tests whether correct pileup function is called when obs/exp pileup is dispatched"""
        test_df_interval = pd.DataFrame(
            {0: ["chr1", "chr1"], 1: [0, 1000], 2: [100000, 200000]}
        )
        mock_read_csv.return_value = test_df_interval
        mock_Cooler.return_value = "mock_cooler"
        mock_get_expected.return_value = pd.DataFrame()
        # dispatch call
        _do_pileup_variable_size(self.cooler, 5, "testpath", self.arms, "Obs/Exp")
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
        mock_np,
    ):
        """Tests whether correct pileup function is called when obs/exp pileup is dispatched"""
        test_df_interval = pd.DataFrame(
            {0: ["chr1", "chr1"], 1: [0, 1000], 2: [100000, 200000]}
        )
        mock_read_csv.return_value = test_df_interval
        mock_Cooler.return_value = "mock_cooler"
        mock_get_expected.return_value = "expected"
        # dispatch call
        _do_pileup_variable_size(self.cooler, 5, "testpath", self.arms, "ICCF")
        # check whether get_expected was called
        mock_get_expected.assert_not_called()
        mock_pileup_iccf.assert_called()
        # check whether iccf pileup is not called
        mock_pileup_obs_exp.assert_not_called()

    @patch("app.pipeline_worker_functions.pd.read_csv")
    def test_empty_array_returned_if_binsize_none(self, mock_read_csv):
        """Tests an empty array is returned when optimal binsize is none"""
        test_df_interval = pd.DataFrame({0: ["chr1", "chr1"], 1: [0, 0], 2: [100, 200]})
        mock_read_csv.return_value = test_df_interval
        # dispatch call
        result = _do_pileup_variable_size(
            self.cooler, 5, "testpath", "testarms", "ICCF"
        )
        self.assertTrue(np.all(np.isnan(result)))

    @patch(
        "app.pipeline_worker_functions.interval_operations.get_bin_number_for_expanded_intervals"
    )
    @patch("app.pipeline_worker_functions.HT.extract_windows_different_sizes_iccf")
    @patch("app.pipeline_worker_functions.HT.extract_windows_different_sizes_obs_exp")
    @patch("app.pipeline_worker_functions.cooler.Cooler")
    @patch("app.pipeline_worker_functions.pd.read_csv")
    def test_bad_interpolation_regions_skipped(
        self,
        mock_read_csv,
        mock_Cooler,
        mock_pileup_obs_exp,
        mock_pileup_iccf,
        mock_bin_numbers,
    ):
        """tests whether pileup_arrays that are of size [0, 0] are skipped and filled with nans"""
        test_df_interval = pd.DataFrame(
            {0: ["chr1", "chr1"], 1: [0, 1000], 2: [100000, 200000]}
        )
        mock_read_csv.return_value = test_df_interval
        mock_Cooler.return_value = "mock_cooler"
        mock_bin_numbers.return_value = 10
        mock_pileup_iccf.return_value = [np.ones((10, 10)), np.array([])]
        # dispatch call
        result = _do_pileup_variable_size(self.cooler, 5, "testpath", self.arms, "ICCF")
        self.assertTrue(np.allclose(result, np.ones((10, 10))))

    @patch("app.pipeline_worker_functions.get_optimal_binsize")
    def test_regions_with_bad_chromosomes_filled_with_nan(self, mock_binsize):
        """Checks whether regions with bad chromosomes are filled with nans"""
        mock_binsize.return_value = 5000000
        with patch("app.pipeline_worker_functions.pd.read_csv") as mock_read_csv:
            test_df_interval = pd.DataFrame(
                {
                    0: ["chr1", "chrASDF", "chr1", "chrASDF"],
                    1: [50000000, 10, 90000000, 100],
                    2: [70000000, 10, 100000000, 150],
                }
            )
            mock_read_csv.return_value = test_df_interval
            # dispatch call
            result = _do_pileup_variable_size(
                self.cooler, 50, "testpath", self.arms, "ICCF", collapse=False
            )
        test_array_one = np.array([[0.08672944, 0.02488877], [0.02488877, 0.07476589]])
        test_array_two = np.array([[0.10348359, 0.03325665], [0.03325665, 0.12614132]])
        self.assertTrue(np.allclose(result[..., 0], test_array_one))
        self.assertTrue(np.all(np.isnan(result[..., 1])))
        self.assertTrue(np.allclose(result[..., 2], test_array_two))
        self.assertTrue(np.all(np.isnan(result[..., 3])))

    def test_cooler_w_missing_resolutions_return_nans_w_collapse(self):
        """Tests whether calling pileup on a cooler with
        a binsize that is not available returns an array of nans
        with the right shape according to windowsize and binsize"""
        arms = pd.read_csv(self.app.config["CHROM_ARMS"])
        with patch("app.pipeline_worker_functions.pd.read_csv") as mock_read_csv:
            test_df_interval = pd.DataFrame(
                {
                    0: ["chr1"],
                    1: [0],
                    2: [100000],
                }
            )
            mock_read_csv.return_value = test_df_interval
            # dispatch call
            result = _do_pileup_variable_size(
                self.cooler, 1, "testpath", arms, "ICCF", collapse=True
            )
        self.assertEqual(result.shape, (140, 140))
        self.assertTrue(np.all(np.isnan(result)))

    def test_cooler_w_missing_resolutions_return_nans_wo_collapse(self):
        """Tests whether calling pileup on a cooler with
        a binsize that is not available returns an array of nans
        with the right shape according to windowsize and binsize"""
        arms = pd.read_csv(self.app.config["CHROM_ARMS"])
        with patch("app.pipeline_worker_functions.pd.read_csv") as mock_read_csv:
            test_df_interval = pd.DataFrame(
                {
                    0: ["chr1", "chr1"],
                    1: [60000000, 10000],
                    2: [60000000, 10000],
                }
            )
            mock_read_csv.return_value = test_df_interval
            # dispatch call
            result = _do_pileup_variable_size(
                self.cooler, 1, "testpath", arms, "ICCF", collapse=False
            )
        self.assertEqual(result.shape, (140, 140, 2))
        self.assertTrue(np.all(np.isnan(result)))

    @patch("app.pipeline_worker_functions.get_optimal_binsize")
    @patch("app.pipeline_worker_functions.HT.get_expected")
    def test_cached_obs_exp_used(self, mock_expected, mock_binsize):
        """Tests whether cached obs/exp dataset is used"""
        mock_binsize.return_value = 5000000
        arms = pd.read_csv(self.app.config["CHROM_ARMS"])
        obs_exp = ObsExp(
            dataset_id=self.cooler.id,
            binsize=5000000,
            filepath=os.path.join("./tests/testfiles", "expected.csv"),
        )
        db.session.add(obs_exp)
        db.session.commit()
        # create mock regions
        test_df_interval = pd.DataFrame(
            {
                0: ["chr1", "chr1"],
                1: [60000000, 10000],
                2: [60000000, 10000],
            }
        )
        mock_path = os.path.join(self.app.config["UPLOAD_DIR"], "mock_regions.csv")
        test_df_interval.to_csv(mock_path, index=False, header=None, sep="\t")
        # dispatch call
        _do_pileup_variable_size(
            self.cooler, 1, mock_path, arms, "Obs/Exp", collapse=False
        )
        mock_expected.assert_not_called()

    @patch("app.pipeline_worker_functions.get_optimal_binsize")
    def test_calculated_obs_exp_cached(self, mock_binsize):
        mock_binsize.return_value = 5000000
        """Tests whether cached obs/exp dataset is created if it does not exist already"""
        arms = pd.read_csv(self.app.config["CHROM_ARMS"])
        # create mock regions
        test_df_interval = pd.DataFrame(
            {
                0: ["chr1", "chr1"],
                1: [60000000, 10000],
                2: [60000000, 10000],
            }
        )
        mock_path = os.path.join(self.app.config["UPLOAD_DIR"], "mock_regions.csv")
        test_df_interval.to_csv(mock_path, index=False, header=None, sep="\t")
        # dispatch call
        _do_pileup_variable_size(
            self.cooler, 1, mock_path, arms, "Obs/Exp", collapse=False
        )
        self.assertEqual(1, len(ObsExp.query.all()))
        ds = ObsExp.query.first()
        self.assertEqual(ds.dataset_id, self.cooler.id)
        self.assertEqual(ds.binsize, 5000000)
        # load ds
        expected = pd.read_csv(os.path.join("./tests/testfiles", "expected.csv"))
        calculated = pd.read_csv(ds.filepath)
        assert_frame_equal(expected, calculated)


class TestGetOptimalBinsize(LoginTestCase):
    """Tests get_optimal_binsize helper function"""

    def test_none_if_regions_too_small(self):
        """tests if none is returned if regions are too small."""
        regions = pd.DataFrame({"chrom": ["chr1"], "start": [0], "end": [10]})
        self.assertEqual(get_optimal_binsize(regions, 100, self.app.config["PREPROCESSING_MAP"]), None)

    def test_none_if_regions_too_large(self):
        """tests if none is returned if regions too large"""
        regions = pd.DataFrame({"chrom": ["chr1"], "start": [0], "end": [10 ** 9]})
        self.assertEqual(get_optimal_binsize(regions, 100, self.app.config["PREPROCESSING_MAP"]), None)

    def test_correct_binsize_small_size(self):
        """tests correct handling of small regions."""
        regions = pd.DataFrame({"chrom": ["chr1"], "start": [0], "end": [10000]})
        self.assertEqual(get_optimal_binsize(regions, 100, self.app.config["PREPROCESSING_MAP"]), 5000)

    def test_correct_binsize_moderate_size(self):
        """tests correct handling of moderately sized regions."""
        regions = pd.DataFrame({"chrom": ["chr1"], "start": [0], "end": [500001]})
        self.assertEqual(get_optimal_binsize(regions, 100, self.app.config["PREPROCESSING_MAP"]), 5000)

    def test_correct_binsize_large_size(self):
        """tests correct handling of large regions."""
        regions = pd.DataFrame({"chrom": ["chr1"], "start": [0], "end": [1000001]})
        self.assertEqual(get_optimal_binsize(regions, 100, self.app.config["PREPROCESSING_MAP"]), 10000)

    def test_correct_binsize_rare_large_size(self):
        """tests correct handling of small regions with rare lare regions"""
        regions = pd.DataFrame(
            {
                "chrom": ["chr1"] * 100,
                "start": [0] * 100,
                "end": [10000] * 99 + [1000001],
            }
        )
        self.assertEqual(get_optimal_binsize(regions, 100, self.app.config["PREPROCESSING_MAP"]), 5000)

    def test_correct_binsize_tads(self):
        """tests correct handling of small regions with rare lare regions"""
        regions = pd.read_csv(
            "tests/testfiles/G2_tads_w_size.bed", sep="\t", header=None
        ).rename(columns={0: "chrom", 1: "start", 2: "end"})
        self.assertEqual(get_optimal_binsize(regions, 100, self.app.config["PREPROCESSING_MAP"]), 10000)

    def test_correct_binsize_tads_low_number_target_bins(self):
        """tests correct handling of small regions with rare lare regions"""
        regions = pd.read_csv(
            "tests/testfiles/G2_tads_w_size.bed", sep="\t", header=None
        ).rename(columns={0: "chrom", 1: "start", 2: "end"})
        self.assertEqual(get_optimal_binsize(regions, 50, self.app.config["PREPROCESSING_MAP"]), 20000)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
