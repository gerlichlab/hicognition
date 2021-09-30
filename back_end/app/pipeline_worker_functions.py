"""Worker functions for pipeline steps that 
perform the actual calculations and database state
changes"""
import os
import logging
import pandas as pd
import numpy as np
import umap
from flask.globals import current_app
from skimage.transform import resize
from ngs import HiCTools as HT
import cooler
import bbi
from hicognition import io_helpers, interval_operations
import bioframe as bf
from sklearn.impute import SimpleImputer
import pylola
from .api.helpers import remove_safely, get_optimal_binsize
from . import db
from .models import (
    Assembly,
    AverageIntervalData,
    Collection,
    IndividualIntervalData,
    AssociationIntervalData,
    EmbeddingIntervalData,
)

# get logger
log = logging.getLogger("rq.worker")


# Data handling


def _do_pileup_fixed_size(
    cooler_dataset, window_size, binsize, regions_path, arms, pileup_type
):
    """do pileup with subsequent averaging for regions with a fixed size"""
    # open cooler
    cooler_file = cooler.Cooler(cooler_dataset.file_path + f"::/resolutions/{binsize}")
    # load regions and search for center
    regions = pd.read_csv(regions_path, sep="\t", header=None)
    regions = regions.rename(columns={0: "chrom", 1: "start", 2: "end"})
    regions.loc[:, "pos"] = (regions["start"] + regions["end"]) // 2
    # assing regions to support
    pileup_windows = HT.assign_regions(
        window_size, int(binsize), regions["chrom"], regions["pos"], arms
    ).dropna()
    # do pileup
    if pileup_type == "Obs/Exp":
        expected = HT.get_expected(
            cooler_file, arms, proc=current_app.config["OBS_EXP_PROCESSES"]
        )
        pileup_array = HT.do_pileup_obs_exp(
            cooler_file,
            expected,
            pileup_windows,
            proc=current_app.config["PILEUP_PROCESSES"],
        )
    else:
        pileup_array = HT.do_pileup_iccf(
            cooler_file, pileup_windows, proc=current_app.config["PILEUP_PROCESSES"]
        )
    return pileup_array


def _do_pileup_variable_size(cooler_dataset, binsize, regions_path, arms, pileup_type):
    """do pileup with subsequent averaging for regions with a variable size"""
    # load regions
    regions = pd.read_csv(regions_path, sep="\t", header=None)
    regions = regions.rename(columns={0: "chrom", 1: "start", 2: "end"})
    # search for optimal binsize
    bin_number_expanded = interval_operations.get_bin_number_for_expanded_intervals(
        binsize, current_app.config["VARIABLE_SIZE_EXPANSION_FACTOR"]
    )
    cooler_binsize = get_optimal_binsize(regions, bin_number_expanded)
    log.info(f"      Optimal binsize is {cooler_binsize}")
    if cooler_binsize is None:
        empty = np.empty((bin_number_expanded, bin_number_expanded))
        empty[:] = np.nan
        return empty
    cooler_file = cooler.Cooler(
        cooler_dataset.file_path + f"::/resolutions/{cooler_binsize}"
    )
    # expand regions
    pileup_regions = interval_operations.expand_regions(
        regions, current_app.config["VARIABLE_SIZE_EXPANSION_FACTOR"]
    )
    if pileup_type == "Obs/Exp":
        expected = HT.get_expected(
            cooler_file, arms, proc=current_app.config["OBS_EXP_PROCESSES"]
        )
        pileup_arrays = HT.extract_windows_different_sizes_obs_exp(
            pileup_regions, arms, cooler_file, expected
        )
    else:
        pileup_arrays = HT.extract_windows_different_sizes_iccf(
            pileup_regions, arms, cooler_file
        )
    # resize to fit
    resized_arrays = []
    for array in pileup_arrays:
        # replace inf with nan
        array[np.isinf(array)] = np.nan
        if len(array) != 0:
            resized_arrays.append(
                resize(array, (bin_number_expanded, bin_number_expanded))
            )
        else:
            empty = np.empty((bin_number_expanded, bin_number_expanded))
            empty[:] = np.nan
            resized_arrays.append(empty)
    stacked = np.stack(resized_arrays, axis=2)
    return np.nanmean(stacked, axis=2)


def _do_stackup_fixed_size(bigwig_filepath, regions, window_size, binsize):
    regions = regions.rename(columns={0: "chrom", 1: "start", 2: "end"})
    regions.loc[:, "pos"] = (regions["start"] + regions["end"]) // 2
    # construct stackup-regions: positions - windowsize until position + windowsize
    stackup_regions = pd.DataFrame(
        {
            "chrom": regions["chrom"],
            "start": regions["pos"]
            - window_size,  # regions outside of chromosomes will be filled with NaN by pybbi
            "end": regions["pos"] + window_size,
        }
    )
    # calculate number of bins
    bin_number = int(window_size / binsize) * 2
    # make target array
    target_array = np.empty((len(stackup_regions), bin_number))
    target_array.fill(np.nan)
    # filter stackup_regions for chromoosmes that are in bigwig
    chromosome_names = bbi.chromsizes(bigwig_filepath).keys()
    is_good_chromosome = [
        True if chrom in chromosome_names else False
        for chrom in stackup_regions["chrom"]
    ]
    good_chromosome_indices = np.arange(len(stackup_regions))[is_good_chromosome]
    good_regions = stackup_regions.iloc[good_chromosome_indices, :]
    # extract data
    stackup_array = bbi.stackup(
        bigwig_filepath,
        chroms=good_regions["chrom"].to_list(),
        starts=good_regions["start"].to_list(),
        ends=good_regions["end"].to_list(),
        bins=bin_number,
        missing=np.nan,
    )
    # put extracted data back in target array
    target_array[good_chromosome_indices, :] = stackup_array
    return target_array


def _do_stackup_variable_size(bigwig_filepath, regions, binsize):
    regions = regions.rename(columns={0: "chrom", 1: "start", 2: "end"})
    stackup_regions = interval_operations.expand_regions(
        regions, current_app.config["VARIABLE_SIZE_EXPANSION_FACTOR"]
    )
    bin_number = interval_operations.get_bin_number_for_expanded_intervals(
        binsize, current_app.config["VARIABLE_SIZE_EXPANSION_FACTOR"]
    )
    # make target array
    target_array = np.empty((len(stackup_regions), bin_number))
    target_array.fill(np.nan)
    # filter stackup_regions for chromoosmes that are in bigwig
    chromosome_names = bbi.chromsizes(bigwig_filepath).keys()
    is_good_chromosome = [
        True if chrom in chromosome_names else False
        for chrom in stackup_regions["chrom"]
    ]
    good_chromosome_indices = np.arange(len(stackup_regions))[is_good_chromosome]
    good_regions = stackup_regions.iloc[good_chromosome_indices, :]
    # extract data
    stackup_array = bbi.stackup(
        bigwig_filepath,
        chroms=good_regions["chrom"].to_list(),
        starts=good_regions["start"].to_list(),
        ends=good_regions["end"].to_list(),
        bins=bin_number,
        missing=np.nan,
    )
    # put extracted data back in target array
    target_array[good_chromosome_indices, :] = stackup_array
    return target_array


def _do_enrichment_calculations_fixed_size(
    collection_id, window_size, binsize, regions_path
):
    """Lola enrichment calculations for fixed size regions"""
    regions = (
        pd.read_csv(regions_path, sep="\t", header=None)
        .iloc[:, [0, 1, 2]]
        .rename(columns={0: "chrom", 1: "start", 2: "end"})
    )
    # make queries
    log.info("      Constructing queries...")
    # get chromosome sizes -> this will be the same for all datasets of the collection
    assembly = Assembly.query.get(
        Collection.query.get(collection_id).datasets[0].assembly
    )
    chromsizes = io_helpers.load_chromsizes(assembly.chrom_sizes)
    chromsizes_regions = pd.DataFrame(
        {"chrom": chromsizes.index, "start": 0, "end": chromsizes}
    )
    # filter based on whether the original regions are in chromosomes
    filtered = (
        bf.count_overlaps(regions, chromsizes_regions)
        .query("count > 0")
        .drop("count", axis="columns")
    )
    queries = interval_operations.chunk_intervals(filtered, window_size, binsize)
    filtered_queries = [
        bf.count_overlaps(query, chromsizes_regions)
        .query("count > 0")
        .drop("count", axis="columns")
        .drop_duplicates()
        .reset_index(drop=True)
        for query in queries
    ]
    # get target datasets
    log.info("      Calculate target list...")
    collection = Collection.query.get(collection_id)
    target_list = [
        pd.read_csv(target.file_path, sep="\t", header=None)
        .iloc[:, [0, 1, 2]]
        .rename(columns={0: "chrom", 1: "start", 2: "end"})
        for target in collection.datasets
    ]
    filtered_target_list = [
        bf.count_overlaps(target, chromsizes_regions)
        .query("count > 0")
        .drop("count", axis="columns")
        .drop_duplicates()
        .reset_index(drop=True)
        for target in target_list
    ]
    # get universe -> genome binned with equal binsize
    universe = bf.binnify(chromsizes, binsize)
    # perform enrichment analysis
    log.info("      Run enrichment analysis...")
    results = [
        pylola.run_lola(query, filtered_target_list, universe, processes=4)[
            "odds_ratio"
        ].values
        for query in filtered_queries
    ]
    # stack results
    return np.stack(results, axis=1)


def _do_enrichment_calculations_variable_size(collection_id, binsize, regions_path):
    """Lola enrichment calculations for variably size regions"""
    regions = (
        pd.read_csv(regions_path, sep="\t", header=None)
        .iloc[:, [0, 1, 2]]
        .rename(columns={0: "chrom", 1: "start", 2: "end"})
    )
    # make queries
    log.info("      Constructing queries...")
    # get chromosome sizes -> this will be the same for all datasets of the collection
    assembly = Assembly.query.get(
        Collection.query.get(collection_id).datasets[0].assembly
    )
    chromsizes = io_helpers.load_chromsizes(assembly.chrom_sizes)
    chromsizes_regions = pd.DataFrame(
        {"chrom": chromsizes.index, "start": 0, "end": chromsizes}
    )
    # filter based on whether the original regions are in chromosomes
    filtered = (
        bf.count_overlaps(regions, chromsizes_regions)
        .query("count > 0")
        .drop("count", axis="columns")
    )
    queries = interval_operations.chunk_intervals_variable_size(
        filtered, binsize, current_app.config["VARIABLE_SIZE_EXPANSION_FACTOR"]
    )
    filtered_queries = [
        bf.count_overlaps(query, chromsizes_regions)
        .query("count > 0")
        .drop("count", axis="columns")
        .drop_duplicates()
        .reset_index(drop=True)
        for query in queries
    ]
    # get target datasets
    log.info("      Calculate target list...")
    collection = Collection.query.get(collection_id)
    target_list = [
        pd.read_csv(target.file_path, sep="\t", header=None)
        .iloc[:, [0, 1, 2]]
        .rename(columns={0: "chrom", 1: "start", 2: "end"})
        for target in collection.datasets
    ]
    filtered_target_list = [
        bf.count_overlaps(target, chromsizes_regions)
        .query("count > 0")
        .drop("count", axis="columns")
        .drop_duplicates()
        .reset_index(drop=True)
        for target in target_list
    ]
    # get universe -> union of queries
    universe = pd.concat(queries).drop_duplicates().reset_index(drop=True)
    # perform enrichment analysis
    log.info("      Run enrichment analysis...")
    results = [
        pylola.run_lola(query, filtered_target_list, universe, processes=4)[
            "odds_ratio"
        ].values
        for query in filtered_queries
    ]
    # stack results
    return np.stack(results, axis=1)


def _do_embedding_1d_fixed_size(collection_id, intervals_id, binsize):
    features = Collection.query.get(collection_id).datasets
    data = []
    for feature in features:
        stackup = IndividualIntervalData.query.filter(
            (IndividualIntervalData.dataset_id == feature.id)
            & (IndividualIntervalData.intervals_id == intervals_id)
            & (IndividualIntervalData.binsize == binsize)
        ).first()
        temp = np.load(stackup.file_path)
        # load data and extract center column if data is point feature
        data.append(temp[:, temp.shape[1] // 2])
    # construct feature frame
    feature_frame = np.stack(data).transpose()
    # do imputation
    imputed_frame = SimpleImputer().fit_transform(feature_frame)
    # calculate embedding
    log.info("      Running embedding...")
    embedder = umap.UMAP(random_state=42)
    return embedder.fit_transform(imputed_frame), feature_frame


def _do_embedding_1d_variable_size(collection_id, intervals_id, binsize):
    features = Collection.query.get(collection_id).datasets
    data = []
    for feature in features:
        stackup = IndividualIntervalData.query.filter(
            (IndividualIntervalData.dataset_id == feature.id)
            & (IndividualIntervalData.intervals_id == intervals_id)
            & (IndividualIntervalData.binsize == binsize)
        ).first()
        temp = np.load(stackup.file_path)
        # Take area between the expanded regions
        start_index = int(
            (current_app.config["VARIABLE_SIZE_EXPANSION_FACTOR"] * 100) // binsize
        )
        end_index = int(start_index + (100 // binsize))
        reduced = np.mean(temp[:, start_index:end_index], axis=1)
        data.append(reduced)
    # construct feature frame
    feature_frame = np.stack(data).transpose()
    # do imputation
    imputed_frame = SimpleImputer().fit_transform(feature_frame)
    # calculate embedding
    log.info("      Running embedding...")
    embedder = umap.UMAP(random_state=42)
    return embedder.fit_transform(imputed_frame), feature_frame


# Database handling


def _add_embedding_1d_to_db(
    file_path, file_path_features, binsize, intervals_id, collection_id
):
    """Adds association data set to db"""
    # check if old association interval data exists and delete them
    test_query = EmbeddingIntervalData.query.filter(
        (EmbeddingIntervalData.binsize == int(binsize))
        & (EmbeddingIntervalData.intervals_id == intervals_id)
        & (EmbeddingIntervalData.collection_id == collection_id)
    ).all()
    for entry in test_query:
        remove_safely(entry.file_path)
        db.session.delete(entry)
    # add new entry
    new_entry = EmbeddingIntervalData(
        binsize=int(binsize),
        name=os.path.basename(file_path),
        file_path=file_path,
        file_path_feature_values=file_path_features,
        intervals_id=intervals_id,
        collection_id=collection_id,
        value_type="1d-embedding",
    )
    db.session.add(new_entry)
    db.session.commit()


def _add_association_data_to_db(file_path, binsize, intervals_id, collection_id):
    """Adds association data set to db"""
    # check if old association interval data exists and delete them
    test_query = AssociationIntervalData.query.filter(
        (AssociationIntervalData.binsize == int(binsize))
        & (AssociationIntervalData.intervals_id == intervals_id)
        & (AssociationIntervalData.collection_id == collection_id)
    ).all()
    for entry in test_query:
        remove_safely(entry.file_path)
        db.session.delete(entry)
    # add new entry
    new_entry = AssociationIntervalData(
        binsize=int(binsize),
        name=os.path.basename(file_path),
        file_path=file_path,
        intervals_id=intervals_id,
        collection_id=collection_id,
    )
    db.session.add(new_entry)
    db.session.commit()


def _add_stackup_db(
    file_path, file_path_small, binsize, intervals_id, bigwig_dataset_id
):
    """Adds stackup to database"""
    # check if old individual interval data exists and delete them
    test_query = IndividualIntervalData.query.filter(
        (IndividualIntervalData.binsize == int(binsize))
        & (IndividualIntervalData.intervals_id == intervals_id)
        & (IndividualIntervalData.dataset_id == bigwig_dataset_id)
    ).all()
    for entry in test_query:
        remove_safely(entry.file_path)
        remove_safely(entry.file_path_small)
        db.session.delete(entry)
    # add new entry
    new_entry = IndividualIntervalData(
        binsize=int(binsize),
        name=os.path.basename(file_path),
        file_path=file_path,
        file_path_small=file_path_small,
        intervals_id=intervals_id,
        dataset_id=bigwig_dataset_id,
    )
    db.session.add(new_entry)
    db.session.commit()


def _add_line_db(file_path, binsize, intervals_id, bigwig_dataset_id):
    """Adds pileup region to database"""
    # check if old average interval data exists and delete them
    test_query = AverageIntervalData.query.filter(
        (AverageIntervalData.binsize == int(binsize))
        & (AverageIntervalData.intervals_id == intervals_id)
        & (AverageIntervalData.dataset_id == bigwig_dataset_id)
    ).all()
    for entry in test_query:
        remove_safely(entry.file_path)
        db.session.delete(entry)
    # add new entry
    new_entry = AverageIntervalData(
        binsize=int(binsize),
        name=os.path.basename(file_path),
        file_path=file_path,
        intervals_id=intervals_id,
        dataset_id=bigwig_dataset_id,
        value_type="line",
    )
    db.session.add(new_entry)
    db.session.commit()


def _add_pileup_db(file_path, binsize, intervals_id, cooler_dataset_id, pileup_type):
    """Adds pileup region to database and deletes any old pileups with the
    same parameter combination."""
    # check if old average interval data exists and delete them
    test_query = AverageIntervalData.query.filter(
        (AverageIntervalData.binsize == int(binsize))
        & (AverageIntervalData.intervals_id == intervals_id)
        & (AverageIntervalData.dataset_id == cooler_dataset_id)
        & (AverageIntervalData.value_type == pileup_type)
    ).all()
    for entry in test_query:
        remove_safely(entry.file_path)
        db.session.delete(entry)
    # add new entry
    new_entry = AverageIntervalData(
        binsize=int(binsize),
        name=os.path.basename(file_path),
        file_path=file_path,
        intervals_id=intervals_id,
        dataset_id=cooler_dataset_id,
        value_type=pileup_type,
    )
    db.session.add(new_entry)
    db.session.commit()