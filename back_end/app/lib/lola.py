"""Worker function for pylola.

Moved from Mittmich/pylola at c3b24ae (pylola/utils.py), the version HiCognition ran,
unchanged but for ruff's formatting and import order. pylola is MIT-licensed; its notice is in LICENSE-pylola beside this file.
"""

from functools import partial
from multiprocessing import Pool

import bioframe as bf
import numpy as np
import pandas as pd
from scipy.stats import fisher_exact

PSEUDOCOUNT = 10**-300


def _get_contingency_table(target, query, universe):
    """calculates contingency table for query, target and universe"""
    # create overlaps
    query_target = bf.count_overlaps(query, target)
    universe_target = bf.count_overlaps(universe, target)
    # calculate elements of contingency table
    query_and_target = len(query_target.query("count > 0"))
    query_but_not_target = len(universe_target.query("count > 0")) - query_and_target
    target_but_not_query = len(query_target.query("count == 0"))
    not_query_not_target = (
        len(universe) - query_and_target - query_but_not_target - target_but_not_query
    )
    return {
        "a": query_and_target,
        "b": query_but_not_target,
        "c": target_but_not_query,
        "d": not_query_not_target,
    }


def _do_enrichment_analysis(row):
    """runs enrichment analysis on contingency table"""
    table = np.array([[row["a"], row["b"]], [row["c"], row["d"]]])
    odds_ratio, p_value = fisher_exact(table, alternative="greater")
    return {
        "odds_ratio": odds_ratio,
        "p_value_log": (-1) * np.log10(p_value + PSEUDOCOUNT),
    }


def run_lola(query, target_list, universe, names=None, processes=2):
    """runs enrichment analysis on query with dataframes in target_list
    spanning the universe."""
    with Pool(processes) as p:
        contingency_list = p.map(
            partial(_get_contingency_table, query=query, universe=universe), target_list
        )
    contingency_frame = pd.DataFrame(contingency_list)
    enrichment_result = contingency_frame.apply(
        _do_enrichment_analysis, axis=1, result_type="expand"
    )
    if names is None:
        return pd.concat((contingency_frame, enrichment_result), axis=1)
    name_frame = pd.DataFrame({"names": names})
    return pd.concat((contingency_frame, enrichment_result, name_frame), axis=1)
