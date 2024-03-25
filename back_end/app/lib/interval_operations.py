"""Operations on genomic intervals."""
import pandas as pd


def chunk_intervals(regions, window_size, binsize):
    """Takes dataframe specifying regions and returns a dataframe for each
    binsize-sized chunk in windowisze. E.g. if regions contains 100 genomic positions,
    windowsize is 100000 and binsize is 10000, then 20 dataframe containing 100 genomic
    positions each will be returned.
    """
    if len(regions.columns) > 2:
        # region definition with start and end
        regions = regions.rename(columns={0: "chrom", 1: "start", 2: "end"})
        regions.loc[:, "pos"] = (regions["start"] + regions["end"]) // 2
    else:
        # region definition with start
        regions = regions.rename(columns={0: "chrom", 1: "pos"})
    # get bounds for chunks
    chroms = regions["chrom"]
    starts = ((regions["pos"] - window_size) // binsize) * binsize
    # construct output
    return [
        pd.DataFrame(
            {
                "chrom": chroms,
                "start": starts + offset,
                "end": starts + offset + binsize,
            }
        )
        for offset in range(0, 2 * window_size, binsize)
    ]


def chunk_intervals_variable_size(regions, binsize, expansion_factor):
    """Takes dataframe specifying regions with start and end and returns a dataframe for each
    binsize-sized (in terms of percentage of the entire region) chunk in [start - size*expansion_factor, end + szie*expansion_factor]
    """
    regions = regions.rename(columns={0: "chrom", 1: "start", 2: "end"})
    sizes = regions["end"] - regions["start"]
    # get bounds for chunks
    chroms = regions["chrom"]
    starts = (regions["start"] - sizes * expansion_factor).astype(int)
    binsizes = (sizes / (100 / binsize)).astype(int)
    bin_number = int((100 + expansion_factor * 100 * 2) / binsize)
    # construct output
    return [
        pd.DataFrame(
            {
                "chrom": chroms,
                "start": starts + offset * binsizes,
                "end": starts + (offset + 1) * binsizes,
            }
        )
        for offset in range(bin_number)
    ]


def get_bin_number_for_expanded_intervals(binsize_perc, expansion_factor):
    """Returns binnumber with bins being the binsize in percentage of the total interval size, before
    expanding it left and right with expansion factor. So if binsize percentage is 10, then the original
    interval contains 10 bins and after expansion with expansion factor e.g. 0.2 2 bins are added left and right
    so the total binnumber will be 14."""
    return int((100 + expansion_factor * 100 * 2) / binsize_perc)


def expand_regions(regions, expansion_factor):
    """Will expand regions by expansion factor left and right"""
    if "chrom" in regions:
        size = regions["end"] - regions["start"]
        return pd.DataFrame(
            {
                "chrom": regions["chrom"],
                "start": (regions["start"] - expansion_factor * size).astype(int),
                "end": (regions["end"] + expansion_factor * size).astype(int),
            }
        )
    size_1 = regions["end1"] - regions["start1"]
    size_2 = regions["end2"] - regions["start2"]
    return pd.DataFrame(
        {
            "chrom1": regions["chrom1"],
            "start1": (regions["start1"] - expansion_factor * size_1).astype(int),
            "end1": (regions["end1"] + expansion_factor * size_1).astype(int),
            "chrom2": regions["chrom2"],
            "start2": (regions["start2"] - expansion_factor * size_2).astype(int),
            "end2": (regions["end2"] + expansion_factor * size_2).astype(int),
        }
    )
