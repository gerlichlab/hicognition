"""Tests for io_helpers.py."""
import unittest
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
            "tests/testfiles/real_data_tricky_header_cleaned.bed", self.chrom_names, []
        )
        self.assertTrue(result)

    def test_real_data_large(self):
        """Tests good bedfile without comment header"""
        result = format_checkers.is_bed_file_correctly_formatted(
            "tests/testfiles/good_data_large.bed", self.chrom_names, []
        )
        self.assertTrue(result)

    def test_real_data_named_columns(self):
        result = format_checkers.is_bed_file_correctly_formatted(
            "tests/testfiles/real_data_tricky_header_named_columns.bed",
            self.chrom_names,
            [],
        )
        self.assertTrue(result)

    def test_real_data_tricky_header(self):
        """Tests format checking of real data with comments in header."""
        result = format_checkers.is_bed_file_correctly_formatted(
            "tests/testfiles/real_data_tricky_header.bed", self.chrom_names, []
        )
        self.assertTrue(result)

    def test_real_data_tricky_header_2(self):
        """Tests formatchecking of bedfile with header containing track and browser"""
        result = format_checkers.is_bed_file_correctly_formatted(
            "tests/testfiles/real_data_tricky_header_w_track_and_browser.bed",
            self.chrom_names,
            [],
        )
        self.assertTrue(result)

    def test_real_data_tricky_header_2_w_named_columns(self):
        """Tests format checking of bed file with comments in header and also including track and browser lines
        as well as named columns."""
        result = format_checkers.is_bed_file_correctly_formatted(
            "tests/testfiles/real_data_tricky_header_named_columns_w_track_and_browser.bed",
            self.chrom_names,
            [],
        )
        self.assertTrue(result)

    def test_bad_data_no_textfile(self):
        """Tests something that is not a textfile."""
        result = format_checkers.is_bed_file_correctly_formatted(
            "tests/testfiles/bad_cooler.mcool", self.chrom_names, []
        )
        self.assertFalse(result)

    def test_bad_data_non_numeric_value_in_column(self):
        """Tests bedfile with  non-numeric values in start/end columns"""
        result = format_checkers.is_bed_file_correctly_formatted(
            "tests/testfiles/non_numeric_values.bed", self.chrom_names, []
        )
        self.assertFalse(result)

    def test_bad_data_unsupported_chromosomes(self):
        """Tests bedfile with unsupported chromosomes"""
        result = format_checkers.is_bed_file_correctly_formatted(
            "tests/testfiles/unsupported_chromosomes.bed", self.chrom_names, []
        )
        self.assertFalse(result)


class TestIsCoolerCorrectlyFormatted(unittest.TestCase):
    """Test suite the check whether cooler is correctly formatted"""

    @classmethod
    def setUp(cls):
        cls.chrom_names = set(
            ["chr" + str(i) for i in range(1, 23)] + ["chrX", "chrY", "chrM"]
        )

    def test_good_cooler(self):
        """Good cooler should return True"""
        self.assertTrue(
            format_checkers.is_mcooler(
                "./tests/testfiles/test.mcool", self.chrom_names, []
            )
        )

    def test_bad_cooler(self):
        """bad cooler should return false"""
        self.assertFalse(
            format_checkers.is_mcooler(
                "./tests/testfiles/bad_cooler.mcool", self.chrom_names, []
            )
        )

    def test_good_cooler_resolution_not_available(self):
        """Good cooler without required resolutions should return false."""
        self.assertFalse(
            format_checkers.is_mcooler(
                "./tests/testfiles/test.mcool", self.chrom_names, [42]
            )
        )


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
