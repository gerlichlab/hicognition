"""Helper functions to read and convert common
data formats."""
import re
import pandas as pd
import numpy as np
import bioframe
import logging
from functools import partial
from .format_checkers import _is_bed_row


def convert_bed_to_bedpe(input_file, target_file, halfwindowsize):
    """Converts bedfile at inputFile to a bedpefile,
    expanding the point of interest up- and downstream
    by halfwindowsize basepairs.

    Only intervals that fall within the bounds of
    chromosomes are written out.
    """
    # load input_file
    input_frame = pd.read_csv(input_file, sep="\t", header=None)
    # handle case that positions are specified in two columns
    if (
        len(input_frame.columns) > 2
    ):  # assuming second and third column hold position info
        input_frame = input_frame.rename(columns={0: "chrom", 1: "start", 2: "end"})
        input_frame.loc[:, "pos"] = (input_frame["start"] + input_frame["end"]) // 2
        temp_frame = input_frame[["chrom", "pos"]]
    else:  # assuming second column holds position info
        input_frame = input_frame.rename(columns={0: "chrom", 1: "pos"})
        temp_frame = input_frame
    # stitch together output frame
    left_pos = temp_frame["pos"] - halfwindowsize
    right_pos = temp_frame["pos"] + halfwindowsize
    half_frame = pd.DataFrame(
        {"chrom": temp_frame["chrom"], "start1": left_pos, "end1": right_pos}
    )
    # filter by chromosome sizes
    chrom_sizes = (
        pd.DataFrame(bioframe.fetch_chromsizes("hg19"))
        .reset_index()
        .rename(columns={"index": "chrom"})
    )
    half_frame_chromo = pd.merge(half_frame, chrom_sizes, on="chrom")
    # generate filter expression
    retained_rows = (half_frame_chromo["start1"] > 0) & (
        half_frame_chromo["end1"] < half_frame_chromo["length"]
    )
    # filter dataframe
    filtered = half_frame_chromo.loc[retained_rows, :].drop(columns=["length"])
    # select row_ids of the original bed-file that are retained
    bed_row_index = np.arange(len(half_frame_chromo))[retained_rows]
    # construct final dataframe and write it to file
    final = pd.concat((filtered, filtered), axis=1)
    # add bed_row_index as final column
    final.loc[:, "bed_row_index"] = bed_row_index
    final.to_csv(target_file, sep="\t", header=None, index=False)


def clean_bed(input_file, output_file):
    """
    Loads in bedfile and removes headers.
    """
    # first, read in the file
    with open(input_file, "r") as f:
        content = f.read()
        lines = content.split("\n")
    # strip comment heade
    skipped_rows = 0
    for line in lines:
        if (line[0] == "#") or (line[:5] == "track") or (line[:7] == "browser"):
            skipped_rows += 1
            continue
        break
    file_accumulator = []
    # check whether next line contains column names -> first three columns will contain chrSomething number number
    potential_header_line = lines[skipped_rows]
    split_header = potential_header_line.split("\t")
    if not _is_bed_row(split_header):
        # header present
        skipped_rows += 1
    stripped_lines = lines[skipped_rows:]
    for line in stripped_lines:
        if line == "":
            # Skip empty last line
            continue
        file_accumulator.append(line.split("\t"))
    # construct dataframe and save
    data = pd.DataFrame(file_accumulator)
    data.to_csv(output_file, sep="\t", index=False, header=None)


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
