"""Tests for io_helpers.py."""
import unittest
import shutil
import os
import pandas as pd
from pandas.testing import assert_frame_equal
from hicognition import io_helpers


class TestConvertBedToBedPE(unittest.TestCase):
    """Tests to check conversion from bed
    to bedpe with a given windowsize."""

    def setUp(self):
        """setup test environment."""
        # make test directory
        os.mkdir("./tmp_test")
        self.tempdir = "./tmp_test"

    def tearDown(self):
        """remove test directory"""
        shutil.rmtree("./tmp_test")

    def test_small_single_column(self):
        """Tests conversion of a small synthetic file to
        a correct bedpe file. This case
        has a bedfile with a single position column."""
        io_helpers.convert_bed_to_bedpe(
            "tests/testfiles/test_small.bed",
            os.path.join(self.tempdir, "test_small_result.bedpe"),
            halfwindowsize=300000,
        )
        # load expected data
        expected = pd.read_csv(
            "tests/testfiles/test_small.bedpe", sep="\t", header=None
        )
        # load result
        result = pd.read_csv(
            os.path.join(self.tempdir, "test_small_result.bedpe"), sep="\t", header=None
        )
        # compare
        assert_frame_equal(expected, result)

    def test_small_two_columns(self):
        """Tests conversion of a small real data file to
        a correct bedpe file. This case
        has a bedfile with a two position columns."""
        io_helpers.convert_bed_to_bedpe(
            "tests/testfiles/test2_realData_twocol.bed",
            os.path.join(self.tempdir, "test2_realData_twocol.bedpe"),
            halfwindowsize=300000,
        )
        # load expected data
        expected = pd.read_csv("tests/testfiles/test2_realData_twocol.bedpe", sep="\t")
        # load result
        result = pd.read_csv(
            os.path.join(self.tempdir, "test2_realData_twocol.bedpe"), sep="\t"
        )
        # compare
        assert_frame_equal(expected, result)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
