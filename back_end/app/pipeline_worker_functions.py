"""Worker functions for pipeline steps that
perform the actual calculations and database state
changes"""
import os
import logging
import uuid
import pandas as pd
import numpy as np
import umap
from flask.globals import current_app
from skimage.transform import resize
from ngs import HiCTools as HT
import cooler
import bbi
import bioframe as bf
from sklearn.impute import SimpleImputer
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pylola
from . import lib as hicognition
from .lib import io_helpers, interval_operations, feature_extraction
from .lib.utils import get_optimal_binsize
from . import db
from .models import (
    Assembly,
    AverageIntervalData,
    Collection,
    IndividualIntervalData,
    AssociationIntervalData,
    EmbeddingIntervalData,
    ObsExp,
)

# get logger
log = logging.getLogger("rq.worker")


# Data handling


def _do_pileup_fixed_size(
    cooler_dataset,
    window_size,
    binsize,
    regions_path,
    arms,
    pileup_type,
    collapse=True,
    dimension="1d",
):
    """do pileup with subsequent averaging for regions with a fixed size"""
    # load regions and search for center, dependent on dimensions of region
    if dimension == "1d":
        regions = pd.read_csv(regions_path, sep="\t", header=None)
        regions = regions.rename(columns={0: "chrom", 1: "start", 2: "end"})
        regions.loc[:, "pos"] = (regions["start"] + regions["end"]) // 2
    else:
        regions = pd.read_csv(regions_path, sep="\t", header=None)
        regions = regions.rename(
            columns={
                0: "chrom1",
                1: "start1",
                2: "end1",
                3: "chrom2",
                4: "start2",
                5: "end2",
            }
        )
        regions.loc[:, "pos1"] = (regions["start1"] + regions["end1"]) // 2
        regions.loc[:, "pos2"] = (regions["start2"] + regions["end2"]) // 2
    # open cooler and check whether resolution is defined, if not return empty array
    try:
        cooler_file = cooler.Cooler(
            cooler_dataset.file_path + f"::/resolutions/{binsize}"
        )
    except KeyError:
        output_shape = (2 * window_size) // binsize
        if collapse:
            return np.full((output_shape, output_shape), np.nan)
        return np.full((output_shape, output_shape, len(regions)), np.nan)
    # assing regions to support
    if dimension == "1d":
        pileup_windows = HT.assign_regions(
            window_size, int(binsize), regions["chrom"], regions["pos"], arms
        )
    else:
        pileup_windows = HT.assign_regions_2d(
            window_size,
            int(binsize),
            regions["chrom1"],
            regions["pos1"],
            regions["chrom2"],
            regions["pos2"],
            arms,
        )
    # create placeholder with nans
    good_indices = ~pileup_windows.region.isnull().values
    pileup_windows = pileup_windows.dropna()
    # do pileup
    if pileup_type == "Obs/Exp":
        # check whether obs_exp exists
        if (
            obs_exp_entry := cooler_dataset.obs_exp.filter(
                ObsExp.binsize == binsize
            ).first()
        ) is not None:
            # binsize exists
            expected = pd.read_csv(obs_exp_entry.filepath)
        else:
            try:
                expected = HT.get_expected(
                    cooler_file, arms, proc=current_app.config["OBS_EXP_PROCESSES"]
                )
            # Catches KeyError: 'Balancing weight {weight_name} not found!'
            except KeyError:
                output_shape = (2 * window_size) // binsize
                if collapse:
                    return np.full((output_shape, output_shape), np.nan)
                return np.full((output_shape, output_shape, len(regions)), np.nan)
            file_path = os.path.join(
                current_app.config["UPLOAD_DIR"], uuid.uuid4().hex + ".csv"
            )
            expected.to_csv(file_path, index=False)
            new_obs_exp_ds = ObsExp(
                dataset_id=cooler_dataset.id, binsize=binsize, filepath=file_path
            )
            db.session.add(new_obs_exp_ds)
            db.session.commit()
        pileup_array = HT.do_pileup_obs_exp(
            cooler_file,
            expected,
            pileup_windows,
            proc=current_app.config["PILEUP_PROCESSES"],
            collapse=collapse,
        )
    else:
        try:
            pileup_array = HT.do_pileup_iccf(
                cooler_file,
                pileup_windows,
                proc=current_app.config["PILEUP_PROCESSES"],
                collapse=collapse,
            )
        # catches ValueError: No column 'bins/weight'found
        except ValueError:
            output_shape = (2 * window_size) // binsize
            if collapse:
                return np.full((output_shape, output_shape), np.nan)
            return np.full((output_shape, output_shape, len(regions)), np.nan)
    # put togehter output if collapse is false
    # DEBUG TODO
    if collapse is False:
        pileup_shape = pileup_array[..., 0].shape[0]
        output = np.empty((pileup_shape, pileup_shape, len(regions)))
        output.fill(np.nan)
        output[..., good_indices] = pileup_array
    else:
        output = pileup_array
    return output


def _do_pileup_variable_size(
    cooler_dataset,
    binsize,
    regions_path,
    arms,
    pileup_type,
    collapse=True,
    dimension="1d",
):
    """do pileup with subsequent averaging for regions with a variable size"""
    # load regions
    regions = pd.read_csv(regions_path, sep="\t", header=None)
    if dimension == "1d":
        regions = regions.rename(columns={0: "chrom", 1: "start", 2: "end"})
    else:
        regions = regions.rename(
            columns={
                0: "chrom1",
                1: "start1",
                2: "end1",
                3: "chrom2",
                4: "start2",
                5: "end2",
            }
        )
    # search for optimal binsize
    bin_number_expanded = interval_operations.get_bin_number_for_expanded_intervals(
        binsize, current_app.config["VARIABLE_SIZE_EXPANSION_FACTOR"]
    )
    cooler_binsize = get_optimal_binsize(
        regions, bin_number_expanded, current_app.config["PREPROCESSING_MAP"]
    )
    log.info(f"      Optimal binsize is {cooler_binsize}")
    if cooler_binsize is None:
        if collapse:
            return np.full((bin_number_expanded, bin_number_expanded), np.nan)
        return np.full((bin_number_expanded, bin_number_expanded, len(regions)), np.nan)
    # open cooler and check whether resolution is defined, if not return empty array
    try:
        cooler_file = cooler.Cooler(
            cooler_dataset.file_path + f"::/resolutions/{cooler_binsize}"
        )
    except KeyError:
        if collapse:
            return np.full((bin_number_expanded, bin_number_expanded), np.nan)
        return np.full((bin_number_expanded, bin_number_expanded, len(regions)), np.nan)
    # expand regions
    pileup_regions = interval_operations.expand_regions(
        regions, current_app.config["VARIABLE_SIZE_EXPANSION_FACTOR"]
    )
    if pileup_type == "Obs/Exp":
        # check whether obs_exp exists
        if (
            obs_exp_entry := cooler_dataset.obs_exp.filter(
                ObsExp.binsize == cooler_binsize
            ).first()
        ) is not None:
            # binsize exists
            expected = pd.read_csv(obs_exp_entry.filepath)
        else:
            expected = HT.get_expected(
                cooler_file, arms, proc=current_app.config["OBS_EXP_PROCESSES"]
            )
            file_path = os.path.join(
                current_app.config["UPLOAD_DIR"], uuid.uuid4().hex + ".csv"
            )
            expected.to_csv(file_path, index=False)
            new_obs_exp_ds = ObsExp(
                dataset_id=cooler_dataset.id, binsize=cooler_binsize, filepath=file_path
            )
            db.session.add(new_obs_exp_ds)
            db.session.commit()
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
    # fill in bad indices
    assigned_regions = HT._assign_supports(pileup_regions, bf.parse_regions(arms))
    good_indices = ~assigned_regions.region.isnull().values
    pileup_shape = stacked[..., 0].shape[0]
    output = np.empty((pileup_shape, pileup_shape, len(regions)))
    output.fill(np.nan)
    output[..., good_indices] = stacked
    if collapse:
        return np.nanmean(output, axis=2)
    else:
        return output


def _do_stackup_fixed_size(
    bigwig_filepath, regions, window_size, binsize, region_side=None
):
    if region_side is None:
        regions = regions.rename(columns={0: "chrom", 1: "start", 2: "end"})
    elif region_side == "left":
        regions = regions.rename(
            columns={
                0: "chrom",
                1: "start",
                2: "end",
                3: "chrom2",
                4: "start2",
                5: "end2",
            }
        )
    elif region_side == "right":
        regions = regions.rename(
            columns={
                0: "chrom1",
                1: "start1",
                2: "end1",
                3: "chrom",
                4: "start",
                5: "end",
            }
        )
    else:
        raise ValueError(f"region_side parameter {region_side} not understood")
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
    # if no good chromosomes found, try to remove chr suffix
    if not any(is_good_chromosome):
        stackup_regions.loc[:, "chrom"] = [
            entry.strip("chr") for entry in stackup_regions["chrom"]
        ]
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


def _do_stackup_variable_size(bigwig_filepath, regions, binsize, region_side=None):
    if region_side is None:
        regions = regions.rename(columns={0: "chrom", 1: "start", 2: "end"})
    elif region_side == "left":
        regions = regions.rename(
            columns={
                0: "chrom",
                1: "start",
                2: "end",
                3: "chrom2",
                4: "start2",
                5: "end2",
            }
        )
    elif region_side == "right":
        regions = regions.rename(
            columns={
                0: "chrom1",
                1: "start1",
                2: "end1",
                3: "chrom",
                4: "start",
                5: "end",
            }
        )
    else:
        raise ValueError(f"region_side parameter {region_side} not understood")
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
    collection_id, window_size, binsize, regions_path, region_side
):
    """Lola enrichment calculations for fixed size regions"""
    regions = pd.read_csv(regions_path, sep="\t", header=None)
    if region_side is None:
        regions = regions.rename(columns={0: "chrom", 1: "start", 2: "end"})
    elif region_side == "left":
        regions = regions[[0, 1, 2]].rename(columns={0: "chrom", 1: "start", 2: "end"})
    elif region_side == "right":
        regions = regions[[3, 4, 5]].rename(columns={3: "chrom", 4: "start", 5: "end"})
    else:
        raise ValueError(f"region_side parameter {region_side} not understood")
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


def _do_enrichment_calculations_variable_size(
    collection_id, binsize, regions_path, region_side
):
    """Lola enrichment calculations for variably size regions"""
    regions = pd.read_csv(regions_path, sep="\t", header=None)
    if region_side is None:
        regions = regions.rename(columns={0: "chrom", 1: "start", 2: "end"})
    elif region_side == "left":
        regions = regions[[0, 1, 2]].rename(columns={0: "chrom", 1: "start", 2: "end"})
    elif region_side == "right":
        regions = regions[[3, 4, 5]].rename(columns={3: "chrom", 4: "start", 5: "end"})
    else:
        raise ValueError(f"region_side parameter {region_side} not understood")
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


def _do_embedding_1d_fixed_size(collection_id, intervals_id, binsize, region_side):
    features = Collection.query.get(collection_id).datasets
    data = []
    for feature in features:
        stackup = IndividualIntervalData.query.filter(
            (IndividualIntervalData.dataset_id == feature.id)
            & (IndividualIntervalData.intervals_id == intervals_id)
            & (IndividualIntervalData.binsize == binsize)
            & (IndividualIntervalData.region_side == region_side)
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
    embedding = embedder.fit_transform(imputed_frame)
    # do clustering and extract values
    log.info("      Running clustering large...")
    kmeans_large = KMeans(
        n_clusters=current_app.config["CLUSTER_NUMBER_LARGE"], random_state=0
    ).fit(embedding)
    cluster_ids_large = kmeans_large.labels_
    log.info("      Generating average values large...")
    scaled = StandardScaler().fit_transform(imputed_frame)
    average_cluster_values_large = (
        pd.DataFrame(scaled).groupby(cluster_ids_large).mean().values
    )
    log.info("      Running clustering small...")
    kmeans_large = KMeans(
        n_clusters=current_app.config["CLUSTER_NUMBER_SMALL"], random_state=0
    ).fit(embedding)
    cluster_ids_small = kmeans_large.labels_
    log.info("      Generating average values small...")
    average_cluster_values_small = (
        pd.DataFrame(scaled).groupby(cluster_ids_small).mean().values
    )
    return {
        "embedding": embedding,
        "clusters": {
            "large": {
                "cluster_ids": cluster_ids_large,
                "average_values": average_cluster_values_large,
            },
            "small": {
                "cluster_ids": cluster_ids_small,
                "average_values": average_cluster_values_small,
            },
        },
        "features": feature_frame,
    }


def _do_embedding_1d_variable_size(collection_id, intervals_id, binsize, region_side):
    features = Collection.query.get(collection_id).datasets
    data = []
    for feature in features:
        stackup = IndividualIntervalData.query.filter(
            (IndividualIntervalData.dataset_id == feature.id)
            & (IndividualIntervalData.intervals_id == intervals_id)
            & (IndividualIntervalData.binsize == binsize)
            & (IndividualIntervalData.region_side == region_side)
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
    embedding = embedder.fit_transform(imputed_frame)
    # do clustering and extract values
    log.info("      Running clustering large...")
    kmeans_large = KMeans(
        n_clusters=current_app.config["CLUSTER_NUMBER_LARGE"], random_state=0
    ).fit(embedding)
    cluster_ids_large = kmeans_large.labels_
    log.info("      Generating average values large...")
    scaled = StandardScaler().fit_transform(imputed_frame)
    average_cluster_values_large = (
        pd.DataFrame(scaled).groupby(cluster_ids_large).mean().values
    )
    log.info("      Running clustering small...")
    kmeans_large = KMeans(
        n_clusters=current_app.config["CLUSTER_NUMBER_SMALL"], random_state=0
    ).fit(embedding)
    cluster_ids_small = kmeans_large.labels_
    log.info("      Generating average values small...")
    average_cluster_values_small = (
        pd.DataFrame(scaled).groupby(cluster_ids_small).mean().values
    )
    return {
        "embedding": embedding,
        "clusters": {
            "large": {
                "cluster_ids": cluster_ids_large,
                "average_values": average_cluster_values_large,
            },
            "small": {
                "cluster_ids": cluster_ids_small,
                "average_values": average_cluster_values_small,
            },
        },
        "features": feature_frame,
    }


def _do_embedding_2d(data):
    """Embeds examples in the n x k array into a 2-dimensional space
    using umap."""
    # transpose data
    data = data.T
    # extract features
    log.info("      Extracting image features...")
    image_features = feature_extraction.extract_image_features(
        data, pixel_target=(10, 10)
    )
    # check if bad image features and return empty arrays if so
    if image_features is None:
        return {
            "embedding": np.full((len(data), 2), np.nan),
            "clusters": {
                "large": {
                    "cluster_ids": np.full((len(data)), np.nan),
                    "thumbnails": np.full(
                        (
                            current_app.config["CLUSTER_NUMBER_LARGE"],
                            data[0].shape[0],
                            data[0].shape[1],
                        ),
                        np.nan,
                    ),
                },
                "small": {
                    "cluster_ids": np.full((len(data)), np.nan),
                    "thumbnails": np.full(
                        (
                            current_app.config["CLUSTER_NUMBER_SMALL"],
                            data[0].shape[0],
                            data[0].shape[1],
                        ),
                        np.nan,
                    ),
                },
            },
        }
    # calculate embedding
    log.info("      Running embedding...")
    embedder = umap.UMAP(random_state=42)
    try:
        embedding = embedder.fit_transform(image_features)
    except:
        # TODO: fix nicer
        log.info("      Embedding failed!")
        return {
            "embedding": np.full((len(data), 2), np.nan),
            "clusters": {
                "large": {
                    "cluster_ids": np.full((len(data)), np.nan),
                    "thumbnails": np.full(
                        (
                            current_app.config["CLUSTER_NUMBER_LARGE"],
                            data[0].shape[0],
                            data[0].shape[1],
                        ),
                        np.nan,
                    ),
                },
                "small": {
                    "cluster_ids": np.full((len(data)), np.nan),
                    "thumbnails": np.full(
                        (
                            current_app.config["CLUSTER_NUMBER_SMALL"],
                            data[0].shape[0],
                            data[0].shape[1],
                        ),
                        np.nan,
                    ),
                },
            },
        }
    #  kmeans clustering
    log.info("      Running clustering large...")
    kmeans_large = KMeans(
        n_clusters=current_app.config["CLUSTER_NUMBER_LARGE"], random_state=0
    ).fit(embedding)
    cluster_ids_large = kmeans_large.labels_
    # create thumbnails for each cluster
    log.info("      Generating thumbnails large...")
    thumbnails_list = []
    for cluster in range(current_app.config["CLUSTER_NUMBER_LARGE"]):
        sub_stacks = np.stack(
            [
                array
                for index, array in enumerate(data)
                if cluster_ids_large[index] == cluster
            ],
            axis=2,
        )
        thumbnail = np.nanmean(sub_stacks, axis=2)
        thumbnails_list.append(thumbnail)
    thumbnails_large = np.stack(thumbnails_list, axis=0)
    #  kmeans clustering
    log.info("      Running clustering small...")
    kmeans_small = KMeans(
        n_clusters=current_app.config["CLUSTER_NUMBER_SMALL"], random_state=0
    ).fit(embedding)
    cluster_ids_small = kmeans_small.labels_
    # create thumbnails for each cluster
    log.info("      Generating thumbnails small...")
    thumbnails_list = []
    for cluster in range(current_app.config["CLUSTER_NUMBER_SMALL"]):
        sub_stacks = np.stack(
            [
                array
                for index, array in enumerate(data)
                if cluster_ids_small[index] == cluster
            ],
            axis=2,
        )
        thumbnail = np.nanmean(sub_stacks, axis=2)
        thumbnails_list.append(thumbnail)
    thumbnails_small = np.stack(thumbnails_list, axis=0)
    return {
        "embedding": embedding,
        "clusters": {
            "large": {
                "cluster_ids": cluster_ids_large,
                "thumbnails": thumbnails_large,
            },
            "small": {
                "cluster_ids": cluster_ids_small,
                "thumbnails": thumbnails_small,
            },
        },
    }


# Database handling


def _add_embedding_2d_to_db(
    filepaths, binsize, intervals_id, dataset_id, interaction_type, cluster_number
):
    """Adds association data set to db"""
    # check if old association interval data exists and delete them
    entry = EmbeddingIntervalData.query.filter(
        (EmbeddingIntervalData.binsize == int(binsize))
        & (EmbeddingIntervalData.intervals_id == intervals_id)
        & (EmbeddingIntervalData.dataset_id == dataset_id)
        & (EmbeddingIntervalData.normalization == interaction_type)
        & (EmbeddingIntervalData.cluster_number == cluster_number)
    ).first()
    if entry is not None:
        hicognition.io_helpers.remove_safely(entry.file_path, current_app.logger)
        hicognition.io_helpers.remove_safely(entry.thumbnail_path, current_app.logger)
        hicognition.io_helpers.remove_safely(entry.cluster_id_path, current_app.logger)
        # update entry
        entry.name = os.path.basename(filepaths["embedding"])
        entry.file_path = filepaths["embedding"]
        entry.thumbnail_path = filepaths["thumbnails"]
        entry.cluster_id_path = filepaths["cluster_ids"]
    else:
        # add new entry
        entry = EmbeddingIntervalData(
            binsize=int(binsize),
            name=os.path.basename(filepaths["embedding"]),
            file_path=filepaths["embedding"],
            thumbnail_path=filepaths["thumbnails"],
            cluster_id_path=filepaths["cluster_ids"],
            intervals_id=intervals_id,
            dataset_id=dataset_id,
            value_type="2d-embedding",
            normalization=interaction_type,
            cluster_number=cluster_number,
        )
        db.session.add(entry)
    db.session.commit()


def _add_embedding_1d_to_db(
    filepaths, binsize, intervals_id, collection_id, cluster_number, region_side
):
    """Adds association data set to db"""
    # check if old association interval data exists and delete them
    entry = EmbeddingIntervalData.query.filter(
        (EmbeddingIntervalData.binsize == int(binsize))
        & (EmbeddingIntervalData.intervals_id == intervals_id)
        & (EmbeddingIntervalData.collection_id == collection_id)
        & (EmbeddingIntervalData.cluster_number == cluster_number)
        & (EmbeddingIntervalData.region_side == region_side)
    ).first()
    if entry is not None:
        hicognition.io_helpers.remove_safely(entry.file_path, current_app.logger)
        hicognition.io_helpers.remove_safely(
            entry.file_path_feature_values, current_app.logger
        )
        hicognition.io_helpers.remove_safely(entry.cluster_id_path, current_app.logger)
        hicognition.io_helpers.remove_safely(entry.thumbnail_path, current_app.logger)
        entry.name = os.path.basename(filepaths["embedding"])
        entry.file_path = filepaths["embedding"]
        entry.file_path_feature_values = filepaths["features"]
        entry.cluster_id_path = filepaths["cluster_ids"]
        entry.thumbnail_path = filepaths["average_values"]
    else:
        # add new entry
        entry = EmbeddingIntervalData(
            binsize=int(binsize),
            name=os.path.basename(filepaths["embedding"]),
            file_path=filepaths["embedding"],
            file_path_feature_values=filepaths["features"],
            cluster_id_path=filepaths["cluster_ids"],
            thumbnail_path=filepaths["average_values"],
            intervals_id=intervals_id,
            collection_id=collection_id,
            value_type="1d-embedding",
            cluster_number=cluster_number,
            region_side=region_side,
        )
        db.session.add(entry)
    db.session.commit()


def _add_association_data_to_db(
    file_path, binsize, intervals_id, collection_id, region_side
):
    """Adds association data set to db"""
    # check if old association interval data exists and delete them
    entry = AssociationIntervalData.query.filter(
        (AssociationIntervalData.binsize == int(binsize))
        & (AssociationIntervalData.intervals_id == intervals_id)
        & (AssociationIntervalData.collection_id == collection_id)
        & (AssociationIntervalData.region_side == region_side)
    ).first()
    if entry is not None:
        hicognition.io_helpers.remove_safely(entry.file_path, current_app.logger)
        entry.file_path = file_path
    else:
        # add new entry
        entry = AssociationIntervalData(
            binsize=int(binsize),
            name=os.path.basename(file_path),
            file_path=file_path,
            intervals_id=intervals_id,
            collection_id=collection_id,
            region_side=region_side,
        )
        db.session.add(entry)
    db.session.commit()


def _add_stackup_db(
    file_path,
    file_path_small,
    binsize,
    intervals_id,
    bigwig_dataset_id,
    region_side=None,
):
    """Adds stackup to database"""
    # check if old individual interval data exists and delete them
    entry = IndividualIntervalData.query.filter(
        (IndividualIntervalData.binsize == int(binsize))
        & (IndividualIntervalData.intervals_id == intervals_id)
        & (IndividualIntervalData.dataset_id == bigwig_dataset_id)
        & (IndividualIntervalData.region_side == region_side)
    ).first()
    if entry is not None:
        hicognition.io_helpers.remove_safely(entry.file_path, current_app.logger)
        hicognition.io_helpers.remove_safely(entry.file_path_small, current_app.logger)
        entry.file_path = file_path
        entry.file_path_small = file_path_small
    else:
        # add new entry
        entry = IndividualIntervalData(
            binsize=int(binsize),
            name=os.path.basename(file_path),
            file_path=file_path,
            file_path_small=file_path_small,
            intervals_id=intervals_id,
            dataset_id=bigwig_dataset_id,
            region_side=region_side,
        )
        db.session.add(entry)
    db.session.commit()


def _add_line_db(file_path, binsize, intervals_id, bigwig_dataset_id, region_side=None):
    """Adds pileup region to database"""
    # check if old average interval data exists and delete them
    entry = AverageIntervalData.query.filter(
        (AverageIntervalData.binsize == int(binsize))
        & (AverageIntervalData.intervals_id == intervals_id)
        & (AverageIntervalData.dataset_id == bigwig_dataset_id)
        & (AverageIntervalData.region_side == region_side)
    ).first()
    if entry is not None:
        hicognition.io_helpers.remove_safely(entry.file_path, current_app.logger)
        entry.file_path = file_path
    else:
        # add new entry
        entry = AverageIntervalData(
            binsize=int(binsize),
            name=os.path.basename(file_path),
            file_path=file_path,
            intervals_id=intervals_id,
            dataset_id=bigwig_dataset_id,
            value_type="line",
            region_side=region_side,
        )
        db.session.add(entry)
    db.session.commit()


def _add_pileup_db(file_path, binsize, intervals_id, cooler_dataset_id, pileup_type):
    """Adds pileup region to database and deletes any old pileups with the
    same parameter combination."""
    # check if old average interval data exists and delete them
    entry = AverageIntervalData.query.filter(
        (AverageIntervalData.binsize == int(binsize))
        & (AverageIntervalData.intervals_id == intervals_id)
        & (AverageIntervalData.dataset_id == cooler_dataset_id)
        & (AverageIntervalData.value_type == pileup_type)
    ).first()
    if entry is not None:
        hicognition.io_helpers.remove_safely(entry.file_path, current_app.logger)
        entry.file_path = file_path
    else:
        # add new entry
        entry = AverageIntervalData(
            binsize=int(binsize),
            name=os.path.basename(file_path),
            file_path=file_path,
            intervals_id=intervals_id,
            dataset_id=cooler_dataset_id,
            value_type=pileup_type,
        )
        db.session.add(entry)
    db.session.commit()
