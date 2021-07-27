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
                    "start": [900000, 900010, 900050],
                    "end": [950000, 950010, 950050],
                }
            ),
            pd.DataFrame(
                {
                    "chrom": ["chr1"] * 3,
                    "start": [950000, 950010, 950050],
                    "end": [1000000, 1000010, 1000050],
                }
            ),
            pd.DataFrame(
                {
                    "chrom": ["chr1"] * 3,
                    "start": [1000000, 1000010, 1000050],
                    "end": [1050000, 1050010, 1050050],
                }
            ),
            pd.DataFrame(
                {
                    "chrom": ["chr1"] * 3,
                    "start": [1050000, 1050010, 1050050],
                    "end": [1100000, 1100010, 1100050],
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


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
