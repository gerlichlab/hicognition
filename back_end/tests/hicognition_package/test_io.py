"""Tests the io helpers in the hicognition library."""
import unittest
from unittest.mock import patch
import os
import pandas as pd
from pandas.testing import assert_frame_equal
from tests.test_utils.test_helpers import TempDirTestCase
from app.lib import io_helpers


class TestCleanBed(TempDirTestCase):
    """Tests cleaning a bed-file = stripping it
    from unnecessary headers."""

    def test_real_data_normal(self):
        """Tests cleaning of bed file without any header"""
        io_helpers.clean_bed(
            "tests/testfiles/real_data_tricky_header_cleaned.bed",
            os.path.join(
                TempDirTestCase.TEMP_PATH, "real_data_tricky_header_cleaned.bed"
            ),
        )
        # load expected data
        expected = pd.read_csv(
            "tests/testfiles/real_data_tricky_header_cleaned.bed", sep="\t", header=None
        )
        # load result
        result = pd.read_csv(
            os.path.join(
                TempDirTestCase.TEMP_PATH, "real_data_tricky_header_cleaned.bed"
            ),
            sep="\t",
            header=None,
        )
        # compare
        assert_frame_equal(expected, result)

    def test_real_data_named_columns(self):
        """Tests cleaning of bed file with header that contains named columns"""
        io_helpers.clean_bed(
            "tests/testfiles/real_data_tricky_header_named_columns.bed",
            os.path.join(
                TempDirTestCase.TEMP_PATH, "real_data_tricky_header_cleaned.bed"
            ),
        )
        # load expected data
        expected = pd.read_csv(
            "tests/testfiles/real_data_tricky_header_cleaned.bed", sep="\t", header=None
        )
        # load result
        result = pd.read_csv(
            os.path.join(
                TempDirTestCase.TEMP_PATH, "real_data_tricky_header_cleaned.bed"
            ),
            sep="\t",
            header=None,
        )
        # compare
        assert_frame_equal(expected, result)

    def test_real_data_tricky_header(self):
        """Tests cleaning of bed file with comments in header."""
        io_helpers.clean_bed(
            "tests/testfiles/real_data_tricky_header.bed",
            os.path.join(
                TempDirTestCase.TEMP_PATH, "real_data_tricky_header_cleaned.bed"
            ),
        )
        # load expected data
        expected = pd.read_csv(
            "tests/testfiles/real_data_tricky_header_cleaned.bed", sep="\t", header=None
        )
        # load result
        result = pd.read_csv(
            os.path.join(
                TempDirTestCase.TEMP_PATH, "real_data_tricky_header_cleaned.bed"
            ),
            sep="\t",
            header=None,
        )
        # compare
        assert_frame_equal(expected, result)

    def test_real_data_tricky_header_2(self):
        """Tests cleaning of bed file with comments in header and also including track and browser lines"""
        io_helpers.clean_bed(
            "tests/testfiles/real_data_tricky_header_w_track_and_browser.bed",
            os.path.join(
                TempDirTestCase.TEMP_PATH, "real_data_tricky_header_cleaned.bed"
            ),
        )
        # load expected data
        expected = pd.read_csv(
            "tests/testfiles/real_data_tricky_header_cleaned.bed", sep="\t", header=None
        )
        # load result
        result = pd.read_csv(
            os.path.join(
                TempDirTestCase.TEMP_PATH, "real_data_tricky_header_cleaned.bed"
            ),
            sep="\t",
            header=None,
        )
        # compare
        assert_frame_equal(expected, result)

    def test_real_data_tricky_header_2_w_named_columns(self):
        """Tests cleaning of bed file with comments in header and also including track and browser lines
        as well as named columns."""
        io_helpers.clean_bed(
            "tests/testfiles/real_data_tricky_header_named_columns_w_track_and_browser.bed",
            os.path.join(
                TempDirTestCase.TEMP_PATH, "real_data_tricky_header_cleaned.bed"
            ),
        )
        # load expected data
        expected = pd.read_csv(
            "tests/testfiles/real_data_tricky_header_cleaned.bed", sep="\t", header=None
        )
        # load result
        result = pd.read_csv(
            os.path.join(
                TempDirTestCase.TEMP_PATH, "real_data_tricky_header_cleaned.bed"
            ),
            sep="\t",
            header=None,
        )
        # compare
        assert_frame_equal(expected, result)


class TestCleanBedPe(TempDirTestCase):
    """Tests cleaning a bedpe-file = stripping it
    from unnecessary headers."""

    def test_real_data_normal(self):
        """Tests cleaning of bed file without any header"""
        io_helpers.clean_bedpe(
            "tests/testfiles/real_data_tricky_header_cleaned.bedpe",
            os.path.join(
                TempDirTestCase.TEMP_PATH, "real_data_tricky_header_cleaned.bedpe"
            ),
        )
        # load expected data
        expected = pd.read_csv(
            "tests/testfiles/real_data_tricky_header_cleaned.bedpe", sep="\t", header=None
        )
        # load result
        result = pd.read_csv(
            os.path.join(
                TempDirTestCase.TEMP_PATH, "real_data_tricky_header_cleaned.bedpe"
            ),
            sep="\t",
            header=None,
        )
        # compare
        assert_frame_equal(expected, result)

    def test_real_data_named_columns(self):
        """Tests cleaning of bed file with header that contains named columns"""
        io_helpers.clean_bedpe(
            "tests/testfiles/real_data_tricky_header_named_columns.bedpe",
            os.path.join(
                TempDirTestCase.TEMP_PATH, "real_data_tricky_header_cleaned.bedpe"
            ),
        )
        # load expected data
        expected = pd.read_csv(
            "tests/testfiles/real_data_tricky_header_cleaned.bedpe", sep="\t", header=None
        )
        # load result
        result = pd.read_csv(
            os.path.join(
                TempDirTestCase.TEMP_PATH, "real_data_tricky_header_cleaned.bedpe"
            ),
            sep="\t",
            header=None,
        )
        # compare
        assert_frame_equal(expected, result)

    def test_real_data_tricky_header(self):
        """Tests cleaning of bed file with comments in header."""
        io_helpers.clean_bedpe(
            "tests/testfiles/real_data_tricky_header.bedpe",
            os.path.join(
                TempDirTestCase.TEMP_PATH, "real_data_tricky_header_cleaned.bedpe"
            ),
        )
        # load expected data
        expected = pd.read_csv(
            "tests/testfiles/real_data_tricky_header_cleaned.bedpe", sep="\t", header=None
        )
        # load result
        result = pd.read_csv(
            os.path.join(
                TempDirTestCase.TEMP_PATH, "real_data_tricky_header_cleaned.bedpe"
            ),
            sep="\t",
            header=None,
        )
        # compare
        assert_frame_equal(expected, result)

    def test_real_data_tricky_header_2(self):
        """Tests cleaning of bed file with comments in header and also including track and browser lines"""
        io_helpers.clean_bedpe(
            "tests/testfiles/real_data_tricky_header_w_track_and_browser.bedpe",
            os.path.join(
                TempDirTestCase.TEMP_PATH, "real_data_tricky_header_cleaned.bedpe"
            ),
        )
        # load expected data
        expected = pd.read_csv(
            "tests/testfiles/real_data_tricky_header_cleaned.bedpe", sep="\t", header=None
        )
        # load result
        result = pd.read_csv(
            os.path.join(
                TempDirTestCase.TEMP_PATH, "real_data_tricky_header_cleaned.bedpe"
            ),
            sep="\t",
            header=None,
        )
        # compare
        assert_frame_equal(expected, result)

    def test_real_data_tricky_header_2_w_named_columns(self):
        """Tests cleaning of bed file with comments in header and also including track and browser lines
        as well as named columns."""
        io_helpers.clean_bedpe(
            "tests/testfiles/real_data_tricky_header_named_columns_w_track_and_browser.bedpe",
            os.path.join(
                TempDirTestCase.TEMP_PATH, "real_data_tricky_header_cleaned.bedpe"
            ),
        )
        # load expected data
        expected = pd.read_csv(
            "tests/testfiles/real_data_tricky_header_cleaned.bedpe", sep="\t", header=None
        )
        # load result
        result = pd.read_csv(
            os.path.join(
                TempDirTestCase.TEMP_PATH, "real_data_tricky_header_cleaned.bedpe"
            ),
            sep="\t",
            header=None,
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

    def test_real_data_tricky_header(self):
        """tests sorting of part of a real dataset with positions specified in twocolumns
        with comments in header."""
        io_helpers.sort_bed(
            "tests/testfiles/real_data_tricky_header.bed",
            os.path.join(
                TempDirTestCase.TEMP_PATH, "real_data_tricky_header_sorted_result.bed"
            ),
            "data/hg19.chrom.sizes",
        )
        # load expected data
        expected = pd.read_csv(
            "tests/testfiles/real_data_tricky_header_sorted.bed", sep="\t", header=None
        )
        # load result
        result = pd.read_csv(
            os.path.join(
                TempDirTestCase.TEMP_PATH, "real_data_tricky_header_sorted_result.bed"
            ),
            sep="\t",
            header=None,
        )
        # compare
        assert_frame_equal(expected, result)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
