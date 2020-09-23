"""Helper functions to read and convert common
data formats."""
import pandas as pd
import bioframe


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
    filtered = half_frame_chromo.loc[
        (half_frame_chromo["start1"] > 0)
        & (half_frame_chromo["end1"] < half_frame_chromo["length"]),
        :,
    ].drop(columns=["length"])
    # construct final dataframe and write it to file
    final = pd.concat((filtered, filtered), axis=1)
    final.to_csv(target_file, sep="\t", header=None, index=False)


def sort_bed(bedfile, chromsizes):
    """Sorts entries in bedfile according to chromsizes and
    writes it to a file."""