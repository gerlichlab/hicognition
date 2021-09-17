"""Pipeline steps for redis queue"""
import os
import uuid
import logging

from flask.globals import current_app
import pandas as pd
from pandas.core.indexes.base import ensure_index
import numpy as np
from sklearn.impute import SimpleImputer
import cooler
import bioframe as bf
import umap
from skimage.transform import resize
from ngs import HiCTools as HT
from hicognition import io_helpers, interval_operations
import pylola
import bbi
from .api.helpers import remove_safely
from rq import get_current_job
from . import db
from .models import (
    Assembly,
    Collection,
    Dataset,
    Intervals,
    AverageIntervalData,
    Task,
    IndividualIntervalData,
    AssociationIntervalData,
    EmbeddingIntervalData,
    dataset_preprocessing_table,
    collections_preprocessing_table
)

# get logger
log = logging.getLogger("rq.worker")


def bed_preprocess_pipeline_step(dataset_id, windowsize):
    """
    Performs bedpe preprocessing pipeline step:
    * Convert bed to bedpe
    * Create downsampled indices
    * add Intervals dataset entry
    """
    log.info(f"  Generating Intervals: {dataset_id} with {windowsize}")
    # get database object
    dataset = Dataset.query.get(dataset_id)
    bed_path = dataset.file_path
    bed = pd.read_csv(bed_path, sep="\t", header=None)
    index_file = os.path.join(
        current_app.config["UPLOAD_DIR"], bed_path.split(os.sep)[-1] + "_indices.npy"
    )
    if len(bed) < current_app.config["STACKUP_THRESHOLD"]:
        # if there are less rows than the stackup theshold, index file are the indices of this file
        sub_sample_index = np.arange(len(bed))
    else:
        # set random seed
        np.random.seed(42)
        # subsample
        all_indices = np.arange(len(bed))
        sub_sample_index = np.random.choice(
            all_indices, current_app.config["STACKUP_THRESHOLD"], replace=False
        )
    # store indices
    np.save(index_file, sub_sample_index)
    # Commit to database
    if windowsize == "variable":
        windowsize = None
    new_entry = Intervals(
        dataset_id=dataset_id,
        name=dataset.dataset_name + f"_{windowsize}",
        file_path_sub_sample_index=index_file,
        windowsize=windowsize,
    )
    db.session.add(new_entry)
    db.session.commit()


def perform_pileup(cooler_dataset_id, interval_id, binsize, arms, pileup_type):
    """Performs pileup [either ICCF or Obs/Exp; parameter passed to pileup_type] of cooler_dataset on
    intervals with resolution binsize."""
    log.info(
        f"  Doing pileup on cooler {cooler_dataset_id} with intervals { interval_id} on binsize {binsize}"
    )
    cooler_dataset = Dataset.query.get(cooler_dataset_id)
    intervals = Intervals.query.get(interval_id)
    # get path to dataset
    file_path = intervals.source_dataset.file_path
    # load bedfile
    log.info("      Loading regions...")
    regions = pd.read_csv(file_path, sep="\t", header=None)
    regions = regions.rename(columns={0: "chrom", 1: "start", 2: "end"})
    regions.loc[:, "pos"] = (regions["start"] + regions["end"]) // 2
    # do pileup
    log.info("      Doing pileup...")
    # get windowsize
    window_size = intervals.windowsize
    if window_size is not None:
        # check whether windowsize is divisible by binsize
        if window_size % int(binsize) != 0:
            log.warn(
                "      ########### Windowsize and binsize do not match! ##############"
            )
            return
        pileup_array = _do_pileup_fixed_size(cooler_dataset, window_size, binsize, regions, arms, pileup_type)
    else:
        pileup_array = _do_pileup_variable_size(cooler_dataset, binsize, regions, arms, pileup_type)
    # prepare dataframe for js reading1
    log.info("      Writing output...")
    file_name = uuid.uuid4().hex + ".npy"
    file_path = os.path.join(current_app.config["UPLOAD_DIR"], file_name)
    np.save(file_path, pileup_array)
    # add this to database
    log.info("      Adding database entry...")
    add_pileup_db(file_path, binsize, intervals.id, cooler_dataset.id, pileup_type)
    log.info("      Success!")


def perform_stackup(bigwig_dataset_id, intervals_id, binsize):
    """Performs stackup of bigwig dataset over the intervals provided with the indicated binsize.
    Stores result and adds it to database."""
    log.info(
        f"  Doing pileup on bigwig {bigwig_dataset_id} with intervals {intervals_id} on binsize {binsize}"
    )
    bigwig_dataset = Dataset.query.get(bigwig_dataset_id)
    intervals = Intervals.query.get(intervals_id)
    # get path to dataset
    file_path = intervals.source_dataset.file_path
    # get windowsize
    window_size = intervals.windowsize
    # load bedfile
    log.info("      Loading regions...")
    regions = pd.read_csv(file_path, sep="\t", header=None)
    sub_sample_index = np.load(intervals.file_path_sub_sample_index)
    regions_small = regions.iloc[sub_sample_index, :]
    log.info("      Doing stackup...")
    full_size_array = _do_stackup(
        regions, window_size, binsize, bigwig_dataset.file_path
    )
    downsampled_array = _do_stackup(
        regions_small, window_size, binsize, bigwig_dataset.file_path
    )
    # save full length array to file
    log.info("      Writing output...")
    file_uuid = uuid.uuid4().hex
    file_name = file_uuid + ".npy"
    file_name_line = file_uuid + "_line.npy"
    file_path = os.path.join(current_app.config["UPLOAD_DIR"], file_name)
    file_path_line = os.path.join(current_app.config["UPLOAD_DIR"], file_name_line)
    np.save(file_path, full_size_array)
    line_array = np.nanmean(full_size_array, axis=0)
    np.save(file_path_line, line_array)
    # save small array to file
    file_name_small = file_uuid + "_small.npy"
    file_path_small = os.path.join(current_app.config["UPLOAD_DIR"], file_name_small)
    np.save(file_path_small, downsampled_array)
    # add to database
    log.info("      Adding database entry...")
    add_stackup_db(file_path, file_path_small, binsize, intervals.id, bigwig_dataset.id)
    add_line_db(file_path_line, binsize, intervals.id, bigwig_dataset.id)
    log.info("      Success!")


def perform_enrichment_analysis(collection_id, intervals_id, binsize):
    """Pipeline step to perform enrichment analysis"""
    log.info(
        f"Doing enrichment analysis with collection {collection_id} on inverals {intervals_id} with binsize {binsize}"
    )
    # get query regions
    intervals = Intervals.query.get(intervals_id)
    file_path = intervals.source_dataset.file_path
    window_size = intervals.windowsize
    regions = (
        pd.read_csv(file_path, sep="\t", header=None)
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
    stacked = np.stack(results, axis=1)
    # write output
    log.info("      Writing output...")
    file_path = os.path.join(
        current_app.config["UPLOAD_DIR"], uuid.uuid4().hex + ".npy"
    )
    np.save(file_path, stacked)
    # add to database
    add_association_data_to_db(file_path, binsize, intervals_id, collection_id)


def perform_1d_embedding(collection_id, intervals_id, binsize):
    """Performs embedding on each binsize-sized bin of the window specified in intervals_id using
    the features in collection_id"""
    # get all features in collection
    features = Collection.query.get(collection_id).datasets
    # get dataset for intervals
    source_regions = Intervals.query.get(intervals_id).source_dataset
    # extract stackups
    log.info("      Construct feature frame...")
    data = []
    for feature in features:
        stackup = IndividualIntervalData.query.filter(
            (IndividualIntervalData.dataset_id == feature.id)
            & (IndividualIntervalData.intervals_id == intervals_id)
            & (IndividualIntervalData.binsize == binsize)
        ).first()
        temp = np.load(stackup.file_path)
        if source_regions.sizeType == "Interval":
            # Take area between the expanded regions
            start_index = int((current_app.config["VARIABLE_SIZE_EXPANSION_FACTOR"]*100) // binsize)
            end_index = int(start_index + (100//binsize))
            reduced = np.mean(temp[:, start_index:end_index], axis=1)
            data.append(reduced)
        else:
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
    # write output for embedding
    log.info("      Writing output...")
    file_path = os.path.join(
        current_app.config["UPLOAD_DIR"], uuid.uuid4().hex + "_embedding.npy"
    )
    np.save(file_path, embedding)
    # write output for feature_overlay
    file_path_features = os.path.join(
        current_app.config["UPLOAD_DIR"], uuid.uuid4().hex + "_features.npy"
    )
    np.save(file_path_features, feature_frame)
    # add to database
    add_embedding_1d_to_db(
        file_path, file_path_features, binsize, intervals_id, collection_id
    )


def add_embedding_1d_to_db(
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


def add_association_data_to_db(file_path, binsize, intervals_id, collection_id):
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


def add_stackup_db(
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


def add_line_db(file_path, binsize, intervals_id, bigwig_dataset_id):
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


def add_pileup_db(file_path, binsize, intervals_id, cooler_dataset_id, pileup_type):
    """Adds pileup region to database and deletes any old pileups with the same parameter combination."""
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


def _do_pileup_fixed_size(cooler_dataset, window_size, binsize, regions, arms, pileup_type):
    """do pileup with subsequent averaging for regions with a fixed size"""
    cooler_file = cooler.Cooler(cooler_dataset.file_path + f"::/resolutions/{binsize}")
    pileup_windows = HT.assign_regions(
        window_size, int(binsize), regions["chrom"], regions["pos"], arms
    ).dropna()
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


def _do_pileup_variable_size(cooler_dataset, binsize, regions, arms, pileup_type):
    """do pileup with subsequent averaging for regions with a variable size"""
    # TODO: select resolution based on max/median/min size
    cooler_file = cooler.Cooler(cooler_dataset.file_path + f"::/resolutions/10000")
    # expand regions
    size = regions["end"] - regions["start"]
    pileup_regions = pd.DataFrame(
        {
            "chrom": regions["chrom"],
            "start": (regions["start"] - current_app.config["VARIABLE_SIZE_EXPANSION_FACTOR"] * size).astype(int),
            "end": (regions["end"] + current_app.config["VARIABLE_SIZE_EXPANSION_FACTOR"] * size).astype(int),
        }
    )
    if pileup_type == "Obs/Exp":
        expected = HT.get_expected(
            cooler_file, arms, proc=current_app.config["OBS_EXP_PROCESSES"]
        )
        pileup_arrays = HT.extract_windows_different_sizes_obs_exp(pileup_regions, arms, cooler_file, expected)
    else:
        pileup_arrays = HT.extract_windows_different_sizes_iccf(pileup_regions, arms, cooler_file)
    # resize to fit
    bin_number = int((100 + current_app.config["VARIABLE_SIZE_EXPANSION_FACTOR"]*100*2) / binsize)
    resized_arrays = []
    for array in pileup_arrays:
        # replace inf with nan
        array[np.isinf(array)] = np.nan
        resized_arrays.append(resize(array, (bin_number, bin_number)))
    stacked = np.stack(resized_arrays, axis=2)
    return np.nanmean(stacked, axis=2)


def _do_stackup(regions, window_size, binsize, bigwig_dataset):
    """Takes a set of regions, window_size, binsize as well as the path to a bigwig file and
    extracts data along those regions."""
    regions = regions.rename(columns={0: "chrom", 1: "start", 2: "end"})
    if window_size is not None: # regions with constant size
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
    else: # regions with variable size
        size = regions["end"] - regions["start"]
        stackup_regions = pd.DataFrame(
            {
                "chrom": regions["chrom"],
                "start": regions["start"] - current_app.config["VARIABLE_SIZE_EXPANSION_FACTOR"] * size,
                "end": regions["end"] + current_app.config["VARIABLE_SIZE_EXPANSION_FACTOR"] * size,
            }
        )
        bin_number = int((100 + current_app.config["VARIABLE_SIZE_EXPANSION_FACTOR"]*100*2) / binsize)
    # make arget array
    target_array = np.empty((len(stackup_regions), bin_number))
    target_array.fill(np.nan)
    # filter stackup_regions for chromoosmes that are in bigwig
    chromosome_names = bbi.chromsizes(bigwig_dataset).keys()
    is_good_chromosome = [
        True if chrom in chromosome_names else False
        for chrom in stackup_regions["chrom"]
    ]
    good_chromosome_indices = np.arange(len(stackup_regions))[is_good_chromosome]
    good_regions = stackup_regions.iloc[good_chromosome_indices, :]
    # extract data
    stackup_array = bbi.stackup(
        bigwig_dataset,
        chroms=good_regions["chrom"].to_list(),
        starts=good_regions["start"].to_list(),
        ends=good_regions["end"].to_list(),
        bins=bin_number,
        missing=np.nan,
    )
    # put extracted data back in target array
    target_array[good_chromosome_indices, :] = stackup_array
    return target_array


def _set_dataset_failed(dataset_id, intervals_id):
    """Adds feature dataset associated with dataset_id to failed datasets of region ds associated with intervals_id"""
    log.error("      Preprocessing failed")
    feature = Dataset.query.get(dataset_id)
    region = Intervals.query.get(intervals_id).source_dataset
    log.error(
        f"      Region: {region} with processing features {region.processing_features} and dataset {feature}"
    )
    # remove feature from preprocessing list -> this needs to be done on the association table to avoid concurrency problems
    stmt = dataset_preprocessing_table.delete().where(
        db.and_(
            (dataset_preprocessing_table.c.dataset_region == region.id),
            (dataset_preprocessing_table.c.dataset_feature == feature.id),
        )
    )
    db.session.execute(stmt)
    db.session.commit()
    # add region to failed_features -> if this combination is already in, this operation will fail, but the first one will succeed
    try:
        region.failed_features.append(feature)
        db.session.commit()
    except BaseException as e:
        log.error(e, exc_info=True)
    log.error("      Setting for fail finished")


def _set_collection_failed(collection_id, intervals_id):
    """Adds collection with collection_id to failed collections of region ds associated with intervals"""
    log.error("      Set for fail")
    collection = Collection.query.get(collection_id)
    region = Intervals.query.get(intervals_id).source_dataset
    log.error(
        f"      Region: {region} with processing collections {region.processing_collections} and collection {collection}"
    )
    # remove feature from preprocessing list -> this needs to be done on the association table to avoid concurrency problems
    stmt = collections_preprocessing_table.delete().where(
        db.and_(
            (collections_preprocessing_table.c.dataset_region == region.id),
            (collections_preprocessing_table.c.collection_feature == collection.id),
        )
    )
    db.session.execute(stmt)
    db.session.commit()
    # add region to failed_features -> if this combination is already in, this operation will fail, but the first one will succeed
    try:
        region.failed_collections.append(collection)
        db.session.commit()
    except BaseException as e:
        log.error(e, exc_info=True)
    log.error("      Setting for fail finished")


def _set_collection_finished(collection_id, intervals_id):
    """removes dataset from region associated with intervals_id if no other task is associated with it."""
    region = Intervals.query.get(intervals_id).source_dataset
    associated_tasks = (
        Task.query.join(Intervals)
        .join(Dataset)
        .filter(
            (Dataset.id == region.id)
            & (Task.collection_id == collection_id)
            & (Task.complete == False)
        )
        .all()
    )
    if len(associated_tasks) == 0:
        # current task is last task, remove feature
        stmt = collections_preprocessing_table.delete().where(
            db.and_(
                (collections_preprocessing_table.c.dataset_region == region.id),
                (collections_preprocessing_table.c.collection_feature == collection_id),
            )
        )
        db.session.execute(stmt)
        db.session.commit()


def _set_dataset_finished(dataset_id, intervals_id):
    """removes dataset from region associated with intervals_id if no other task is associated with it."""
    region = Intervals.query.get(intervals_id).source_dataset
    associated_tasks = (
        Task.query.join(Intervals)
        .join(Dataset)
        .filter(
            (Dataset.id == region.id)
            & (Task.dataset_id == dataset_id)
            & (Task.complete == False)
        )
        .all()
    )
    if len(associated_tasks) == 0:
        # current task is last task, remove feature
        stmt = dataset_preprocessing_table.delete().where(
            db.and_(
                (dataset_preprocessing_table.c.dataset_region == region.id),
                (dataset_preprocessing_table.c.dataset_feature == dataset_id),
            )
        )
        db.session.execute(stmt)
        db.session.commit()


def _set_task_progress(progress):
    job = get_current_job()
    if job:
        job.meta["progress"] = progress
        job.save_meta()
        task = Task.query.get(job.get_id())
        if progress >= 100:
            task.complete = True
            db.session.commit()
