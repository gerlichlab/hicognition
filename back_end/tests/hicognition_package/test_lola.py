"""Tests for pylola.

Moved from Mittmich/pylola at c3b24ae with the code it tests. Two of its three region files
are files HiCognition's tests already had: query1.bed is test3_realData_large.bed and
target2.bed is CTCF_peaks.bed.
"""

import unittest

import pandas as pd
from pandas.testing import assert_frame_equal

from app.lib import lola


class TestRunLOLA(unittest.TestCase):
    """Tests for the run_lola functions."""

    @classmethod
    def setUp(cls):
        cls.query1 = pd.read_csv(
            "tests/testfiles/test3_realData_large.bed", sep="\t", header=None
        )[[0, 1, 2]].rename(columns={0: "chrom", 1: "start", 2: "end"})
        cls.target1 = pd.read_csv("tests/testfiles/lola/target1.bed", sep="\t")[
            ["chrom", "start", "end"]
        ]
        cls.target2 = pd.read_csv(
            "tests/testfiles/CTCF_peaks.bed", sep="\t", header=None
        )[[0, 1, 2]].rename(columns={0: "chrom", 1: "start", 2: "end"})
        cls.target_list = [cls.target1, cls.target2]
        cls.universe = pd.concat((cls.query1, cls.target1, cls.target2)).reset_index(
            drop=True
        )

    def test_regions_subsets_of_universe(self):
        """Compares that output of the R LOLA version with pylola
        where query and targets are a subset of universe."""
        result = lola.run_lola(
            self.query1, self.target_list, self.universe, processes=1
        )
        expected = pd.DataFrame(
            {
                "a": [39596, 27201],
                "b": [69997, 71404],
                "c": [919, 13314],
                "d": [1409, 2],
                "odds_ratio": [0.8673024, 6.1035 * 10**-5],
                "p_value_log": [0.0001901352, 0.0000],
            }
        )
        assert_frame_equal(result, expected, check_exact=False, atol=10**-5)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
