"""Helper functions to read and convert common
data formats."""
import pandas as pd
import numpy as np
import os
import logging
from functools import partial

def clean_bedpe(input_file, output_file, chromosome_names=[]):
    """Takes bedpe-file and checks whether it is correctly formated
    expected:
    # comments
    track header
    browser also a header
    chrA   start1   end1   chrB   start2   end2   [...]
    chrA   start1   end1   chrB   start2   end2   [...]
    ...
    """
    headers = ('#', 'track', 'browser')
    with open(input_file, 'r') as f:
        bedpe_file = [line.strip().split('\t') for line in f.readlines() if not line.lower().startswith(headers) and line.strip() != '']
    bedpe_df = pd.DataFrame(bedpe_file, columns=None)
    
    # check for validity, first time may go wrong as header may be in df
    try:
        [bedpe_df.T.iloc[col].astype('str', errors='raise') for col in [0,3]]
        [bedpe_df.T.iloc[col].astype('int', errors='raise') for col in [1,2,4,5]]
    except ValueError:
        bedpe_df.columns = bedpe_df.iloc[0]
        bedpe_df = bedpe_df[1:]
    
    # repeat again with first line as header
    [bedpe_df.T.iloc[col].astype('str') for col in [0,3]]
    [bedpe_df.T.iloc[col].astype('int') for col in [1,2,4,5]]

    chromosomes = set([*bedpe_df.T.iloc[0].unique(), *bedpe_df.T.iloc[3].unique()])
    missing_chromosomes = [chr for chr in chromosomes if chr not in chromosome_names]
    for chr in missing_chromosomes:
        logging.warning(f"Chromosome {chr} does not exist in chromosome names!")
    
    bedpe_df.to_csv(output_file, sep="\t", index=False, header=None)


def clean_bed(input_file, output_file, chromosome_names=[]):
    """
    Loads in bedfile and removes headers, also checks for validity
    """
    headers = ('#', 'track', 'browser')
    with open(input_file, 'r') as f:
        bed_file = [line.strip().split('\t') for line in f.readlines() if not line.lower().startswith(headers) and line.strip() != '']
    bed_df = pd.DataFrame(bed_file, columns=None)
    
    # check for validity, first time may go wrong as header may be in df
    try:
        [bed_df.T.iloc[col].astype('str', errors='raise') for col in [0]]
        [bed_df.T.iloc[col].astype('int', errors='raise') for col in [1,2]]
    except ValueError:
        bed_df.columns = bed_df.iloc[0]
        bed_df = bed_df[1:]
    
    # repeat again with first line as header
    [bed_df.T.iloc[col].astype('str') for col in [0]]
    [bed_df.T.iloc[col].astype('int') for col in [1,2]]

    chromosomes = bed_df.T.iloc[0].unique()
    missing_chromosomes = [chr for chr in chromosomes if chr not in chromosome_names]
    for chr in missing_chromosomes:
        logging.warning(f"Chromosome {chr} does not exist in chromosome names!")
    
    bed_df.to_csv(output_file, sep="\t", index=False, header=None)


def sort_bed(input_file, output_file, chromsizes):
    """Sorts entries in bedfile according to chromsizes and
    writes it to a file. input_file, output_file and chromsizes
    should be a string containing the path to the respective
    files. Will filter chromosomes so that only ones in chromsizes
    are retained."""
    # create helper sort function
    def chromo_sort_function(element, data_unsorted, chromsizes):
        return chromsizes.index(data_unsorted.iloc[element, 0])

    data_unsorted = pd.read_csv(input_file, sep="\t", header=None, comment="#")
    chromsizes = pd.read_csv(chromsizes, sep="\t", header=None)
    # extract chromsizes order as a list for later searching
    chrom_order = chromsizes[0].to_list()
    # handle case that positions are specified in two columns
    if (
        len(data_unsorted.columns) > 2
    ):  # assuming second and third column hold position info
        data_unsorted = data_unsorted.rename(columns={0: "chrom", 1: "start", 2: "end"})
        data_unsorted.loc[:, "pos"] = (
            data_unsorted["start"] + data_unsorted["end"]
        ) // 2
        temp_frame = data_unsorted[["chrom", "pos"]]
    else:  # assuming second column holds position info
        data_unsorted = data_unsorted.rename(columns={0: "chrom", 1: "pos"})
        temp_frame = data_unsorted
    # filter out chromosomes that are not in chromsizes
    data_filtered = temp_frame.loc[temp_frame["chrom"].isin(chrom_order), :]
    # warn that this has happened
    if len(temp_frame) != len(data_filtered):
        filtered_rows = temp_frame.loc[~temp_frame["chrom"].isin(chrom_order), :]
        bad_chroms = " ".join(sorted([i for i in set(filtered_rows["chrom"])]))
        logging.warning(f"Unsupported chromosomes in bedfile: {bad_chroms}")
    # presort data based on genomic positions. Column at index 1 should contain genomic positions.
    genome_pos_sorted = data_filtered.sort_values(by=["pos"])
    # reset index
    genome_pos_sorted.index = range(len(genome_pos_sorted))
    # get sorted index based on chromosome names
    sorted_index = sorted(
        range(len(genome_pos_sorted)),
        key=partial(
            chromo_sort_function,
            data_unsorted=genome_pos_sorted,
            chromsizes=chrom_order,
        ),
    )
    # reorder based on chromosome order
    output = genome_pos_sorted.iloc[sorted_index, :]
    # write to file
    output.to_csv(output_file, sep="\t", index=False, header=None)


def load_chromsizes(path):
    """load chromosome sizes from
    a chromosome sizes file into a series
    with chromosome names as index."""
    chromsize_frame = pd.read_csv(path, sep="\t", header=None)
    chromsize_series = pd.Series(chromsize_frame[1].values, index=chromsize_frame[0])
    return chromsize_series


# TODO handle exceptions better -> e.g. permission problems
def remove_safely(file_path, logger):
    """Tries to remove a file and logs warning with app logger if this does not work."""
    try:
        os.remove(file_path)
    except BaseException:
        logger.warning(f"Tried removing {file_path}, but file does not exist!")
