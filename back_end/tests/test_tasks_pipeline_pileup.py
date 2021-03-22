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
from app.tasks import pipeline_pileup
from app.pipeline_steps import perform_pileup


class TestPipelinePileup(LoginTestCase, TempDirTestCase):
    """Tests whether pipelin_pileup task calls
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
    @patch("app.pipeline_steps.perform_pileup")
    def test_pipeline_pileup_calls_steps_correctly(
        self, mock_perform_pileup, mock_set_progress
    ):
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
        self.assertEqual(
            len(call_args), len(binsizes) * len(pileup_types) * len(intervals_objects)
        )
        # check whether last call to set task progress was 100
        mock_set_progress.assert_called_with(100)


class TestPerformPileup(LoginTestCase, TempDirTestCase):
    def setUp(self):
        """Add test dataset"""
        # call setUp of LoginTestCase to initialize app
        super(TestPerformPileup, self).setUp()
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
        self.dataset2 = Dataset(
            dataset_name="test4",
            file_path="/test/path/test4.mcool",
            higlass_uuid="fdsa87615",
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

    @patch("app.pipeline_steps.add_pileup_db")
    @patch("app.pipeline_steps.export_df_for_js")
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
        mock_export,
        mock_add_db,
    ):
        """Tests whether regions that are defined as chrom, start, end are handled correctly."""
        test_df_interval = pd.DataFrame(
            {0: ["chr1", "chr1"], 1: [0, 1000], 2: [1000, 2000]}
        )
        mock_read_csv.return_value = test_df_interval
        # dispatch call
        arms = pd.read_csv(self.app.config["CHROM_ARMS"])
        perform_pileup(self.dataset, self.intervals1, 10000, arms, "ICCF")
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
    @patch("app.pipeline_steps.export_df_for_js")
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
        mock_export,
        mock_add_db,
    ):
        """Tests whether regions that are defined as chrom, pos are handled correctly."""
        test_df_interval = pd.DataFrame({0: ["chr1", "chr1"], 1: [500, 1500]})
        mock_read_csv.return_value = test_df_interval
        # dispatch call
        arms = pd.read_csv(self.app.config["CHROM_ARMS"])
        perform_pileup(self.dataset, self.intervals1, 10000, arms, "ICCF")
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
    @patch("app.pipeline_steps.export_df_for_js")
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
        mock_export,
        mock_add_db,
    ):
        """Tests whether correct cooler is used for pileup."""
        test_df_interval = pd.DataFrame({0: ["chr1", "chr1"], 1: [500, 1500]})
        mock_read_csv.return_value = test_df_interval
        # dispatch call
        arms = pd.read_csv(self.app.config["CHROM_ARMS"])
        perform_pileup(self.dataset, self.intervals1, 10000, arms, "ICCF")
        # check whether corrrect cooler file was called with correct binsize
        expected_call = self.dataset.file_path + "::/resolutions/10000"
        mock_Cooler.assert_called_with(expected_call)

    @patch("app.pipeline_steps.add_pileup_db")
    @patch("app.pipeline_steps.export_df_for_js")
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
        mock_export,
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
        arms = pd.read_csv(self.app.config["CHROM_ARMS"])
        perform_pileup(self.dataset, self.intervals1, 10000, arms, "Obs/Exp")
        # check whether get_expected was called
        mock_get_expected.assert_called()
        expected_pileup_call = ["mock_cooler", "expected", returned_regions.dropna()]
        mock_pileup_obs_exp.assert_called_with(*expected_pileup_call, proc=1)
        # check whether iccf pileup is not called
        mock_pileup_iccf.assert_not_called()

    @patch("app.pipeline_steps.add_pileup_db")
    @patch("app.pipeline_steps.export_df_for_js")
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
        mock_export,
        mock_add_db,
    ):
        """Tests whether correct cooler is used for pileup."""
        test_df_interval = pd.DataFrame({0: ["chr1", "chr1"], 1: [500, 1500]})
        mock_read_csv.return_value = test_df_interval
        mock_Cooler.return_value = "mock_cooler"
        returned_regions = MagicMock()
        mock_assign_regions.return_value = returned_regions
        # dispatch call
        arms = pd.read_csv(self.app.config["CHROM_ARMS"])
        perform_pileup(self.dataset, self.intervals1, 10000, arms, "ICCF")
        # check whether get_expected was called
        expected_pileup_call = ["mock_cooler", returned_regions.dropna()]
        mock_pileup_iccf.assert_called_with(*expected_pileup_call, proc=1)
        # check whether iccf pileup is not called
        mock_get_expected.assert_not_called()
        mock_pileup_obs_exp.assert_not_called()

    @patch("app.pipeline_steps.uuid.uuid4")
    @patch("app.pipeline_steps.add_pileup_db")
    @patch("app.pipeline_steps.export_df_for_js")
    @patch("app.pipeline_steps.HT.do_pileup_iccf")
    @patch("app.pipeline_steps.HT.do_pileup_obs_exp")
    @patch("app.pipeline_steps.HT.get_expected")
    @patch("app.pipeline_steps.HT.assign_regions")
    @patch("app.pipeline_steps.cooler.Cooler")
    @patch("app.pipeline_steps.pd.read_csv")
    def test_conversion_function_called_correctly(
        self,
        mock_read_csv,
        mock_Cooler,
        mock_assign_regions,
        mock_get_expected,
        mock_pileup_obs_exp,
        mock_pileup_iccf,
        mock_export,
        mock_add_db,
        mock_uuid
    ):
        """Tests whether conversion function as df for java script is called correctly"""
        test_df_interval = pd.DataFrame({0: ["chr1", "chr1"], 1: [500, 1500]})
        mock_read_csv.return_value = test_df_interval
        mock_pileup_iccf.return_value = "testCooler"
        # hack in return value of uuid4().hex to be asdf
        uuid4 = MagicMock()
        type(uuid4).hex = PropertyMock(return_value="asdf")
        mock_uuid.return_value = uuid4
        arms = pd.read_csv(self.app.config["CHROM_ARMS"])
        perform_pileup(self.dataset, self.intervals1, 10000, arms, "ICCF")
        # check whether get_expected was called
        mock_export.assert_called_with("testCooler", self.app.config["UPLOAD_DIR"] + "/asdf.csv")


    @patch("app.pipeline_steps.uuid.uuid4")
    @patch("app.pipeline_steps.add_pileup_db")
    @patch("app.pipeline_steps.export_df_for_js")
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
        mock_export,
        mock_add_db,
        mock_uuid
    ):
        """Tests whether conversion function as df for java script is called correctly"""
        test_df_interval = pd.DataFrame({0: ["chr1", "chr1"], 1: [500, 1500]})
        mock_read_csv.return_value = test_df_interval
        mock_pileup_iccf.return_value = "testCooler"
        # hack in return value of uuid4().hex to be asdf
        uuid4 = MagicMock()
        type(uuid4).hex = PropertyMock(return_value="asdf")
        mock_uuid.return_value = uuid4
        arms = pd.read_csv(self.app.config["CHROM_ARMS"])
        perform_pileup(self.dataset, self.intervals1, 10000, arms, "ICCF")
        # check whether get_expected was called
        mock_add_db.assert_called_with(self.app.config["UPLOAD_DIR"] + "/asdf.csv", 10000, self.intervals1.id, self.dataset.id, "ICCF")


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
