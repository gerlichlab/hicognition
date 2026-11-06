"""Low level accessors for cooler files adpated
from cooltools.snipping

Moved from gerlichlab/ngs at a6f11b5 (tag v0.3b) (ngs/snipping_lib.py), unchanged but for
ruff's formatting and import order. ngs is MIT-licensed;
its notice is in LICENSE-ngs beside this file.
"""

import warnings
from functools import partial

import numpy as np


def flexible_pileup(features, data_select, data_snip, mapper=map):
    """
    TAKEN from cooltool.snipping.pileup -> patched in a fashion that allows differently sized
    windows.
    Handles on-diagonal and off-diagonal cases.
    Parameters
    ----------
    features : DataFrame
        Table of features. Requires columns ['chrom', 'start', 'end'].
        Or ['chrom1', 'start1', 'end1', 'chrom1', 'start2', 'end2'].
        start, end are bp coordinates.
        lo, hi are bin coordinates.
    data_select : callable
        Callable that takes a region as argument and returns
        the data, mask and bin offset of a support region
    data_snip : callable
        Callable that takes data, mask and a 2D bin span (lo1, hi1, lo2, hi2)
        and returns a snippet from the selected support region
    """
    if features.region.isnull().any():
        warnings.warn(
            "Some features do not have regions assigned! Some snips will be empty."
        )

    features = features.copy()
    features["_rank"] = range(len(features))

    cumul_stack = []
    orig_rank = []
    for region_stack, region_ranks in mapper(
        partial(_flexible_pileup, data_select, data_snip),
        features.groupby("region", sort=False),
    ):
        cumul_stack.extend(region_stack)
        orig_rank.extend(region_ranks)
    # restore original rank
    idx = np.argsort(orig_rank)
    sorted_stack = [cumul_stack[i] for i in idx]
    return sorted_stack


def _flexible_pileup(data_select, data_snip, arg):
    """TAKEN from cooltool.snipping._pileup -> patched in a fashion that allows differently sized
    windows."""
    support, feature_group = arg
    # check if support region is on- or off-diagonal
    if len(support) == 2:
        region1, region2 = support[0], support[1]
    else:
        region1 = region2 = support
    # check if features are on- or off-diagonal
    if "start" in feature_group:
        start_1 = feature_group["start"].values
        end_1 = feature_group["end"].values
        start_2, end_2 = start_1, end_1
    else:
        start_1 = feature_group["start1"].values
        end_1 = feature_group["end1"].values
        start_2 = feature_group["start2"].values
        end_2 = feature_group["end2"].values

    data = data_select(region1, region2)
    stack = list(
        map(
            partial(data_snip, data, region1, region2),
            zip(start_1, end_1, start_2, end_2),
        )
    )
    return stack, feature_group["_rank"].values
