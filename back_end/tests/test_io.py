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
            os.path.join(TempDirTestCase.TEMP_PATH, "test_small_result.bedpe"),
            halfwindowsize=300000,
        )
        # load expected data
        expected = pd.read_csv(
            "tests/testfiles/test_small.bedpe", sep="\t", header=None
        )
        # load result
        result = pd.read_csv(
            os.path.join(TempDirTestCase.TEMP_PATH, "test_small_result.bedpe"),
            sep="\t",
            header=None,
        )
        # compare -> don't equate last column, this is bed_row_index and will be checked in later test
        assert_frame_equal(expected, result.iloc[:, :-1])

    def test_small_two_columns(self):
        """Tests conversion of a small real data file to
        a correct bedpe file. This case
        has a bedfile with a two position columns."""
        io_helpers.convert_bed_to_bedpe(
            "tests/testfiles/test2_realData_twocol.bed",
            os.path.join(TempDirTestCase.TEMP_PATH, "test2_realData_twocol.bedpe"),
            halfwindowsize=300000,
        )
        # load expected data
        expected = pd.read_csv(
            "tests/testfiles/test2_realData_twocol.bedpe", sep="\t", header=None
        )
        # load result
        result = pd.read_csv(
            os.path.join(TempDirTestCase.TEMP_PATH, "test2_realData_twocol.bedpe"),
            sep="\t",
            header=None,
        )
        # compare -> don't equate last column, this is bed_row_index and will be checked in later test
        assert_frame_equal(expected, result.iloc[:, :-1])

    def test_bed_row_index_correct_for_filtered_rows(self):
        """Tests whether the retained rows are mapped correctly to original bedfile by bed_row_index"""
        # generate mock bed_file that will be filtered out for certain rows
        test_bed_path = os.path.join(TempDirTestCase.TEMP_PATH, "original.bed")
        test_bed_df = pd.DataFrame(
            {
                "chrom": ["chr1", "chr1", "chr1", "chr1", "chr1"],
                "start": [
                    0,
                    400000,
                    10,
                    600000,
                    249250600,
                ],  # row 0, 2 and 4 should be filtered
                "end": [10, 400010, 20, 600010, 249250610],
            }
        )
        test_bed_df.to_csv(test_bed_path, sep="\t", index=False, header=None)
        # dispatch call
        io_helpers.convert_bed_to_bedpe(
            test_bed_path,
            os.path.join(TempDirTestCase.TEMP_PATH, "filter_output.bedpe"),
            halfwindowsize=300000,
        )
        # load result
        result = pd.read_csv(
            os.path.join(TempDirTestCase.TEMP_PATH, "filter_output.bedpe"),
            sep="\t",
            header=None,
        )
        # check whether result has expected length
        self.assertEqual(len(result), 2)
        # check whether last column is indicate of bed_row_index
        self.assertEqual([1, 3], result.iloc[:, -1].to_list())


class TestSortBed(TempDirTestCase):
    """Tests sorting of bedfiles according to chromosomesizes
    and genomic position."""

    def test_small_data_w_standard_chromos(self):
        """tests sorting of a small test dataset with only
        chromosomes that are named chr${int}"""
        io_helpers.sort_bed(
            "tests/testfiles/test_small.bed",
            os.path.join(TempDirTestCase.TEMP_PATH, "test_small_sorted_result.bed"),
            "data/hg19.chrom.sizes",
        )
        # load expected data
        expected = pd.read_csv(
            "tests/testfiles/test_small_sorted.bed", sep="\t", header=None
        )
        # load result
        result = pd.read_csv(
            os.path.join(TempDirTestCase.TEMP_PATH, "test_small_sorted_result.bed"),
            sep="\t",
            header=None,
        )
        # compare
        assert_frame_equal(expected, result)

    def test_small_data_w_weird_chromos(self):
        """tests sorting of a small test dataset with chromosomes
        that comply to chr${int} as well as chrX and chrY"""
        io_helpers.sort_bed(
            "tests/testfiles/test_small_weird_chromos.bed",
            os.path.join(
                TempDirTestCase.TEMP_PATH, "test_small_sorted_weird_chromos_result.bed"
            ),
            "data/hg19.chrom.sizes",
        )
        # load expected data
        expected = pd.read_csv(
            "tests/testfiles/test_small_weird_chromos_sorted.bed", sep="\t", header=None
        )
        # load result
        result = pd.read_csv(
            os.path.join(
                TempDirTestCase.TEMP_PATH, "test_small_sorted_weird_chromos_result.bed"
            ),
            sep="\t",
            header=None,
        )
        # compare
        assert_frame_equal(expected, result)

    @patch("hicognition.io_helpers.logging.warning")
    def test_small_data_w_bad_chromos(self, mock_logging):
        """tests sorting of a small test dataset with chromosomes
        that comply to chr${int} as well as chrX and chrY"""
        io_helpers.sort_bed(
            "tests/testfiles/test_small_bad_chromos.bed",
            os.path.join(
                TempDirTestCase.TEMP_PATH, "test_small_sorted_bad_chromos_result.bed"
            ),
            "data/hg19.chrom.sizes",
        )
        # load expected data
        expected = pd.read_csv(
            "tests/testfiles/test_small_sorted.bed", sep="\t", header=None
        )
        # load result
        result = pd.read_csv(
            os.path.join(
                TempDirTestCase.TEMP_PATH, "test_small_sorted_bad_chromos_result.bed"
            ),
            sep="\t",
            header=None,
        )
        # compare
        assert_frame_equal(expected, result)
        # assert that warning has been issued
        mock_logging.assert_called_with(
            "Unsupported chromosomes in bedfile: chrA chrB chrD"
        )

    def test_real_data_two_col(self):
        """tests sorting of part of a real dataset with positions specified in twocolumns"""
        io_helpers.sort_bed(
            "tests/testfiles/test2_realData_twocol.bed",
            os.path.join(
                TempDirTestCase.TEMP_PATH, "test2_realData_twocol_sorted_result.bed"
            ),
            "data/hg19.chrom.sizes",
        )
        # load expected data
        expected = pd.read_csv(
            "tests/testfiles/test2_realData_twocol_sorted.bed", sep="\t", header=None
        )
        # load result
        result = pd.read_csv(
            os.path.join(
                TempDirTestCase.TEMP_PATH, "test2_realData_twocol_sorted_result.bed"
            ),
            sep="\t",
            header=None,
        )
        # compare
        assert_frame_equal(expected, result)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
