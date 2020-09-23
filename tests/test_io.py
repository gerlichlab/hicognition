"""Tests for io_helpers.py."""
import unittest
from unittest.mock import patch
import os
import pandas as pd
from pandas.testing import assert_frame_equal
from test_helpers import TempDirTestCase
from hicognition import io_helpers


class TestConvertBedToBedPE(TempDirTestCase):
    """Tests to check conversion from bed
    to bedpe with a given windowsize."""

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


class TestSortBed(TempDirTestCase):
    """Tests sorting of bedfiles according to chromosomesizes
    and genomic position."""

    def test_small_data_w_standard_chromos(self):
        """tests sorting of a small test dataset with only
        chromosomes that are named chr${int}"""
        io_helpers.sort_bed(
            "tests/testfiles/test_small.bed",
             os.path.join(self.tempdir, "test_small_sorted_result.bed"),
             "data/hg19.chrom.sizes"
        )
        # load expected data
        expected = pd.read_csv("tests/testfiles/test_small_sorted.bed", sep="\t", header=None)
        # load result
        result = pd.read_csv(
            os.path.join(self.tempdir, "test_small_sorted_result.bed"), sep="\t", header=None
        )
        # compare
        assert_frame_equal(expected, result)

    def test_small_data_w_weird_chromos(self):
        """tests sorting of a small test dataset with chromosomes
        that comply to chr${int} as well as chrX and chrY"""
        io_helpers.sort_bed(
            "tests/testfiles/test_small_weird_chromos.bed",
             os.path.join(self.tempdir, "test_small_sorted_weird_chromos_result.bed"),
             "data/hg19.chrom.sizes"
        )
        # load expected data
        expected = pd.read_csv("tests/testfiles/test_small_weird_chromos_sorted.bed", sep="\t", header=None)
        # load result
        result = pd.read_csv(
            os.path.join(self.tempdir, "test_small_sorted_weird_chromos_result.bed"), sep="\t", header=None
        )
        # compare
        assert_frame_equal(expected, result)

    @patch("hicognition.io_helpers.logging.warning")
    def test_small_data_w_bad_chromos(self, mock_logging):
        """tests sorting of a small test dataset with chromosomes
        that comply to chr${int} as well as chrX and chrY"""
        io_helpers.sort_bed(
            "tests/testfiles/test_small_bad_chromos.bed",
             os.path.join(self.tempdir, "test_small_sorted_bad_chromos_result.bed"),
             "data/hg19.chrom.sizes"
        )
        # load expected data
        expected = pd.read_csv("tests/testfiles/test_small_sorted.bed", sep="\t", header=None)
        # load result
        result = pd.read_csv(
            os.path.join(self.tempdir, "test_small_sorted_bad_chromos_result.bed"), sep="\t", header=None
        )
        # compare
        assert_frame_equal(expected, result)
        # assert that warning has been issued
        mock_logging.assert_called_with("Unsupported chromosomes in bedfile: chrA chrB chrD")


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
