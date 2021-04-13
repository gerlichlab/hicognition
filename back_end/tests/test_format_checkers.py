"""Tests for io_helpers.py."""
import unittest
from unittest.mock import patch
import os
import pandas as pd
from pandas.testing import assert_frame_equal
from test_helpers import TempDirTestCase
from hicognition import format_checkers


class TestIsBedFileCorrectlyFormatted(TempDirTestCase):
    """Checks for isbedilfecorrectlyformatted"""

    @classmethod
    def setUp(cls):
        cls.chrom_names = set(
            ["chr" + str(i) for i in range(1, 23)] + ["chrX", "chrY", "chrM"]
        )

    def test_real_data_normal(self):
        """Tests good bedfilewithou any header"""
        result = format_checkers.is_bed_file_correctly_formatted(
            "tests/testfiles/real_data_tricky_header_cleaned.bed", self.chrom_names
        )
        self.assertTrue(result)

    def test_real_data_named_columns(self):
        result = format_checkers.is_bed_file_correctly_formatted(
            "tests/testfiles/real_data_tricky_header_named_columns.bed",
            self.chrom_names,
        )
        self.assertTrue(result)

    def test_real_data_tricky_header(self):
        """Tests format checking of real data with comments in header."""
        result = format_checkers.is_bed_file_correctly_formatted(
            "tests/testfiles/real_data_tricky_header.bed", self.chrom_names
        )
        self.assertTrue(result)

    def test_real_data_tricky_header_2(self):
        """Tests formatchecking of bedfile with header containing track and browser"""
        result = format_checkers.is_bed_file_correctly_formatted(
            "tests/testfiles/real_data_tricky_header_w_track_and_browser.bed",
            self.chrom_names,
        )
        self.assertTrue(result)

    def test_real_data_tricky_header_2_w_named_columns(self):
        """Tests format checking of bed file with comments in header and also including track and browser lines
        as well as named columns."""
        result = format_checkers.is_bed_file_correctly_formatted(
            "tests/testfiles/real_data_tricky_header_named_columns_w_track_and_browser.bed",
            self.chrom_names,
        )
        self.assertTrue(result)

    def test_bad_data_no_textfile(self):
        """Tests something that is not a textfile."""
        result = format_checkers.is_bed_file_correctly_formatted(
            "tests/testfiles/bad_cooler.mcool", self.chrom_names
        )
        self.assertFalse(result)

    def test_bad_data_non_numeric_value_in_column(self):
        """Tests bedfile with  non-numeric values in start/end columns"""
        result = format_checkers.is_bed_file_correctly_formatted(
            "tests/testfiles/non_numeric_values.bed", self.chrom_names
        )
        self.assertFalse(result)

    def test_bad_data_unsupported_chromosomes(self):
        """Tests bedfile with unsupported chromosomes"""
        result = format_checkers.is_bed_file_correctly_formatted(
            "tests/testfiles/unsupported_chromosomes.bed", self.chrom_names
        )
        self.assertFalse(result)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
