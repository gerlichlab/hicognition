"""Tests for HiCTools

Moved from gerlichlab/ngs at a6f11b5 (tag v0.3b) with the code it tests. The tests of what
HiCognition doesn't use stayed there, and so did those that need ngs' 42 MB real-data
cooler; the reference results (tests/reference) cover the same code on other data.
"""

import unittest

import cooler
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal, assert_series_equal

from app.lib import hic_tools as HT

# define functions


# define tests


class TestGetExpected(unittest.TestCase):
    """Tests for getting expected diagonal counts from
    a Hi-C matrix."""

    def setUp(self):
        """Setting up common resources"""
        self.cooler = cooler.Cooler(
            "tests/testfiles/ngs/test2.mcool::/resolutions/10000"
        )
        self.arms = pd.DataFrame(
            {"chrom": "chrSyn", "start": 0, "end": 4990000}, index=[0]
        )

    def test_synthetic_data(self):
        """Tests expected counts for synthetic Hi-C data.
        Known values were provided and expected counts for each diagonal
        calculated."""
        result = HT.get_expected(self.cooler, self.arms, proc=1, ignore_diagonals=0)
        check = pd.read_csv("tests/testfiles/ngs/test_expected_chrSyn.csv")
        # merge regions for new expected format
        check.loc[:, "region"] = check.apply(
            lambda x: f"{x['chrom']}:{x['start']}-{x['end']}", axis=1
        )
        check_final = check.drop(columns=["chrom", "start", "end"])[result.columns]
        assert_frame_equal(result, check_final)

    def test_synthetic_data_mult_chroms(self):
        """Tests expected counts for synthetic Hi-C data
        with multiple chromosomal arms. Known values were
        provided and expected counts for each diagonal
        calculated."""
        arms = pd.DataFrame(
            {
                "chrom": ["chrSyn", "chrSyn"],
                "start": [0, 2000000],
                "end": [2000000, 4990000],
            }
        )
        result = HT.get_expected(self.cooler, arms, proc=1, ignore_diagonals=0)
        check = pd.read_csv("tests/testfiles/ngs/test_expected_multiple_chroms.csv")
        # merge regions for new expected format
        check.loc[:, "region"] = check.apply(
            lambda x: f"{x['chrom']}:{x['start']}-{x['end']}", axis=1
        )
        check_final = check.drop(columns=["chrom", "start", "end"])[result.columns]
        assert_frame_equal(result, check_final)


class TestAssignRegions(unittest.TestCase):
    """Tests assigning of chromosomal positions
    to Hi-C bins and chromosomal supports."""

    def setUp(self):
        """Setting up common resources"""
        self.arms = pd.read_csv("tests/testfiles/ngs/arms.csv")

    def test_case1(self):
        """Test assignment of small, synthetic set of regions."""
        bed_file = pd.read_csv("tests/testfiles/ngs/testSmall.bed", sep="\t")
        result = HT.assign_regions(
            window=500000,
            binsize=50000,
            chroms=bed_file["chrom"],
            positions=bed_file["pos"],
            arms=self.arms,
        )
        expected = pd.read_csv("tests/testfiles/ngs/testAssignRegions.csv")
        assert_frame_equal(result, expected)

    def test_case2(self):
        """Test assignment of a different small,
        synthetic set of regions."""
        bed_file = pd.read_csv("tests/testfiles/ngs/testSmall_2.bed", sep="\t")
        result = HT.assign_regions(
            window=500000,
            binsize=50000,
            chroms=bed_file["chrom"],
            positions=bed_file["pos"],
            arms=self.arms,
        )
        expected = pd.read_csv("tests/testfiles/ngs/testAssignRegions_2.csv")
        assert_frame_equal(result, expected)

    def test_region_spans_multiple_supports(self):
        """Tests assign regions when region spans multiple supports."""
        bed_file = pd.read_csv("tests/testfiles/ngs/multiple_support_regions.csv")
        result = HT.assign_regions(
            window=1000000,
            binsize=20000,
            chroms=bed_file["chrom"],
            positions=bed_file["pos"],
            arms=self.arms,
        )
        expected = pd.read_csv(
            "tests/testfiles/ngs/multiple_support_regions_result.csv"
        )
        assert_series_equal(result["region"], expected["region"])

    def test_regions_are_close_to_supports(self):
        """Tests assign regions when regions are close to supports -> bug was found"""
        bed_file = pd.read_csv(
            "tests/testfiles/ngs/regions_close_to_support_boundary.tsv", sep="\t"
        )
        result = HT.assign_regions(
            window=1000000,
            binsize=20000,
            chroms=bed_file["chrom"],
            positions=bed_file["pos"],
            arms=self.arms,
        )
        expected = pd.read_csv(
            "tests/testfiles/ngs/regions_close_to_support_boundary_result.tsv",
            delim_whitespace=True,
        )
        assert_series_equal(result["region"], expected["region"])


class TestPileupICCF(unittest.TestCase):
    """Tests pileup of iteratively corrected counts (ICCF)"""

    def test_no_collapse(self):
        """Tests pileup of synthetic Hi-C data, without collapsing results."""
        position_frame = pd.read_csv("tests/testfiles/ngs/posPileups.csv")
        arms = pd.DataFrame({"chrom": "chrSyn", "start": 0, "end": 4990000}, index=[0])
        assigned = HT.assign_regions(
            50000, 10000, position_frame["chrom"], position_frame["pos"], arms
        )
        cooler_file = cooler.Cooler(
            "tests/testfiles/ngs/test2.mcool::/resolutions/10000"
        )
        result = HT.do_pileup_iccf(cooler_file, assigned, proc=1, collapse=False)
        expected = np.load("tests/testfiles/ngs/test_pileups_iccf_noCollapse.npy")
        self.assertTrue(np.allclose(result, expected))

    def test_collapse(self):
        """Tests pileup of synthetic Hi-C data, with collapsing results."""
        position_frame = pd.read_csv("tests/testfiles/ngs/posPileups.csv")
        arms = pd.DataFrame({"chrom": "chrSyn", "start": 0, "end": 4990000}, index=[0])
        assigned = HT.assign_regions(
            50000, 10000, position_frame["chrom"], position_frame["pos"], arms
        )
        cooler_file = cooler.Cooler(
            "tests/testfiles/ngs/test2.mcool::/resolutions/10000"
        )
        result = HT.do_pileup_iccf(cooler_file, assigned, proc=1, collapse=True)
        expected = np.load("tests/testfiles/ngs/test_pileups_iccf_collapse.npy")
        self.assertTrue(np.allclose(result, expected))


class TestPileupObsExp(unittest.TestCase):
    """Tests pileup of Obs/Exp values."""

    def test_no_collapse(self):
        """Tests pileup of synthetic Hi-C data, without collapsing results."""
        position_frame = pd.read_csv("tests/testfiles/ngs/posPileups.csv")
        arms = pd.DataFrame({"chrom": "chrSyn", "start": 0, "end": 4990000}, index=[0])
        assigned = HT.assign_regions(
            50000, 10000, position_frame["chrom"], position_frame["pos"], arms
        )
        cooler_file = cooler.Cooler(
            "tests/testfiles/ngs/test2.mcool::/resolutions/10000"
        )
        exp_f = HT.get_expected(cooler_file, arms, ignore_diagonals=0)
        result = HT.do_pileup_obs_exp(
            cooler_file, exp_f, assigned, proc=1, collapse=False
        )
        expected = np.load("tests/testfiles/ngs/test_pileups_obsExp_noCollapse.npy")
        self.assertTrue(np.allclose(result, expected))

    def test_collapse(self):
        """Tests pileup of synthetic Hi-C data, with collapsing results."""
        position_frame = pd.read_csv("tests/testfiles/ngs/posPileups.csv")
        arms = pd.DataFrame({"chrom": "chrSyn", "start": 0, "end": 4990000}, index=[0])
        assigned = HT.assign_regions(
            50000, 10000, position_frame["chrom"], position_frame["pos"], arms
        )
        cooler_file = cooler.Cooler(
            "tests/testfiles/ngs/test2.mcool::/resolutions/10000"
        )
        exp_f = HT.get_expected(cooler_file, arms, ignore_diagonals=0)
        result = HT.do_pileup_obs_exp(
            cooler_file, exp_f, assigned, proc=1, collapse=True
        )
        expected = np.load("tests/testfiles/ngs/test_pileups_obsExp_collapse.npy")
        self.assertTrue(np.allclose(result, expected))


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
