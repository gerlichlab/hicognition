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
                {
                    "chrom": ["chr1"] * 3,
                    "start": [900000] * 3,
                    "end": [950000] * 3,
                }
            ),
            pd.DataFrame(
                {
                    "chrom": ["chr1"] * 3,
                    "start": [950000] * 3,
                    "end": [1000000] * 3,
                }
            ),
            pd.DataFrame(
                {
                    "chrom": ["chr1"] * 3,
                    "start": [1000000] * 3,
                    "end": [1050000] * 3,
                }
            ),
            pd.DataFrame(
                {
                    "chrom": ["chr1"] * 3,
                    "start": [1050000] * 3,
                    "end": [1100000] * 3,
                }
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
                {
                    "chrom": ["chr1"],
                    "start": [80 + offset],
                    "end": [80 + offset + 10]
                }
            )
            for offset in range(0, 140, 10)
        ]
        cls.expected_second = [
            pd.DataFrame(
                {
                    "chrom": ["chr6"],
                    "start": [-325000 + offset],
                    "end": [-325000 + offset + 150000]
                }
            )
            for offset in range(0, 4200000, 150000)
        ]

    def test_single_region(self):
        """tests single region"""
        test_region = pd.DataFrame(
            {
                "chrom": ["chr1"],
                "start": [100],
                "end": [200],
            }
        )
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
            {
                "chrom": ["chr6"],
                "start": [275000],
                "end": [3275000],
            }
        )
        # call function
        result = interval_operations.chunk_intervals_variable_size(test_region, 5, 0.2)
        # test length
        self.assertEqual(len(result), len(self.expected_second))
        # test whether chunked frames are correct
        for actual_df, expected_df in zip(result, self.expected_second):
            assert_frame_equal(actual_df, expected_df)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
