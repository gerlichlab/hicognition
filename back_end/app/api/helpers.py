"""Helper functions for api routes"""
import os
from collections import defaultdict
from flask import current_app
from ..models import (
    EmbeddingIntervalData,
    Intervals,
    Dataset,
    Collection,
    Task,
    IndividualIntervalData,
    AverageIntervalData,
    BedFileMetadata,
)
import numpy as np


def update_processing_state(entries, db):
    """updates processing state of all entries (must implement set_processing_state) in the supplied iterable"""
    for entry in entries:
        entry.set_processing_state(db)


def parse_description(form_data):
    if ("description" not in form_data) or (form_data["description"] == "null"):
        description = "No description provided"
    else:
        description = form_data["description"]
    return description


def get_all_interval_ids(region_datasets):
    """Returns ids of all intervals associated with list or region datasets."""
    interval_ids = []
    for region_dataset in region_datasets:
        interval_ids.extend([entry.id for entry in region_dataset.intervals.all()])
    return interval_ids


def parse_binsizes(map, filetype):
    """returns needed binsizes from preprocessing map."""
    binsizes = set()
    for windowsize, bins in map.items():
        if windowsize != "variable":
            binsizes |= set(bins[filetype])
    return list(binsizes)

def get_optimal_binsize(regions, target_bin_number):
    """given a dataframe of regions defined via (chrom, start, end) and a
    target bin number, decide which binsize to use for variable size pileup/enrichment analysis"""
    MAX_CHUNK_NUMBER = 250
    sizes = regions["end"] - regions["start"]
    max_size = np.percentile(sizes, 80)
    median_size = np.median(sizes)
    binsizes = sorted(
        [
            int(entry)
            for entry in parse_binsizes(current_app.config["PREPROCESSING_MAP"], "cooler")
        ]
    )
    chunk_number = [max_size / binsize for binsize in binsizes]
    # check if first chunk_number is below 1 -> should indicate error
    if chunk_number[0] <= 1:
        return None
    # flag binsizes that are below max chunk_number
    good_binsizes = [
        (binsize, median_size / binsize)
        for index, binsize in enumerate(binsizes)
        if chunk_number[index] < MAX_CHUNK_NUMBER
    ]
    # check if any retained
    if len(good_binsizes) == 0:
        return None
    # check which binsize is closest to the target binnumber for the mean size
    best_binsize = min(good_binsizes, key=lambda x: abs(x[1] - target_bin_number))
    # return smallest one that is ok
    return best_binsize[0]


def flatten_and_clean_array(array):
    """takes numpy array and converts it to a list where
    numpy.na and +\- np.inf is convert to python None"""
    return [
        entry if not (np.isnan(entry) or np.isinf(entry)) else None
        for entry in array.flatten()
    ]