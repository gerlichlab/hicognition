"""Tests the interval operations in the hicognition library"""
import unittest
import pandas as pd
from pandas.testing import assert_frame_equal
from hicognition import interval_operations


class TestChunkIntervals(unittest.TestCase):
    """Tests for chunk_intervals"""

    @classmethod
    def setUp(cls):
        cls.expected = [
            pd.DataFrame(
                {"chrom": ["chr1"] * 3, "start": [900000] * 3, "end": [950000] * 3}
            ),
            pd.DataFrame(
                {"chrom": ["chr1"] * 3, "start": [950000] * 3, "end": [1000000] * 3}
            ),
            pd.DataFrame(
                {"chrom": ["chr1"] * 3, "start": [1000000] * 3, "end": [1050000] * 3}
            ),
            pd.DataFrame(
                {"chrom": ["chr1"] * 3, "start": [1050000] * 3, "end": [1100000] * 3}
            ),
        ]

    def test_regions_single_position(self):
        """tests for when regions are defined via
        single column."""
        test_region = pd.DataFrame(
            {"chrom": ["chr1"] * 3, "pos": [1000000, 1000010, 1000050]}
        )
        # call function
        result = interval_operations.chunk_intervals(test_region, 100000, 50000)
        # test length
        self.assertEqual(len(result), 4)
        # test whether chunked frames are correct
        for actual_df, expected_df in zip(result, self.expected):
            assert_frame_equal(actual_df, expected_df)

    def test_regions_dual_position(self):
        """tests for when regions are defined via
        single column."""
        test_region = pd.DataFrame(
            {
                "chrom": ["chr1"] * 3,
                "start": [950000, 950010, 950050],
                "end": [1050000, 1050010, 1050050],
            }
        )
        # call function
        result = interval_operations.chunk_intervals(test_region, 100000, 50000)
        # test length
        self.assertEqual(len(result), 4)
        # test whether chunked frames are correct
        for actual_df, expected_df in zip(result, self.expected):
            assert_frame_equal(actual_df, expected_df)


class TestChunkIntervalsVariableSize(unittest.TestCase):
    """Tests for chunk intervals with variable size."""

    @classmethod
    def setUp(cls):
        cls.expected_first = [
            pd.DataFrame(
                {"chrom": ["chr1"], "start": [80 + offset], "end": [80 + offset + 10]}
            )
            for offset in range(0, 140, 10)
        ]
        cls.expected_second = [
            pd.DataFrame(
                {
                    "chrom": ["chr6"],
                    "start": [-325000 + offset],
                    "end": [-325000 + offset + 150000],
                }
            )
            for offset in range(0, 4200000, 150000)
        ]

    def test_single_region(self):
        """tests single region"""
        test_region = pd.DataFrame({"chrom": ["chr1"], "start": [100], "end": [200]})
        # call function
        result = interval_operations.chunk_intervals_variable_size(test_region, 10, 0.2)
        # test length
        self.assertEqual(len(result), len(self.expected_first))
        # test whether chunked frames are correct
        for actual_df, expected_df in zip(result, self.expected_first):
            assert_frame_equal(actual_df, expected_df)

    def test_region_border_chromosome(self):
        """tests multiple regions"""
        test_region = pd.DataFrame(
            {"chrom": ["chr6"], "start": [275000], "end": [3275000]}
        )
        # call function
        result = interval_operations.chunk_intervals_variable_size(test_region, 5, 0.2)
        # test length
        self.assertEqual(len(result), len(self.expected_second))
        # test whether chunked frames are correct
        for actual_df, expected_df in zip(result, self.expected_second):
            assert_frame_equal(actual_df, expected_df)


class TestGetBinNumberExpandedIntervals(unittest.TestCase):
    """Tests for get_bin_number_for_expanded_intervals"""

    def test_correct_number_produced_large_bins(self):
        """tests large bins"""
        result = interval_operations.get_bin_number_for_expanded_intervals(10, 0.2)
        self.assertEqual(result, 14)

    def test_correct_number_produced_medium_bins(self):
        """tests medium bins"""
        result = interval_operations.get_bin_number_for_expanded_intervals(5, 0.2)
        self.assertEqual(result, 28)

    def test_correct_number_produced_small_bins(self):
        """tests small bins"""
        result = interval_operations.get_bin_number_for_expanded_intervals(1, 0.2)
        self.assertEqual(result, 140)


class TestExpandRegions(unittest.TestCase):
    """Tests for expand regions."""

    def test_regions_correctly_expanded(self):
        """tests if regions are correctly expanded"""
        test_region = pd.DataFrame(
            {"chrom": ["chr1", "chr1"], "start": [100, 200], "end": [200, 400]}
        )
        expected = pd.DataFrame(
            {"chrom": ["chr1", "chr1"], "start": [80, 160], "end": [220, 440]}
        )
        result = interval_operations.expand_regions(test_region, 0.2)
        assert_frame_equal(result, expected)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
