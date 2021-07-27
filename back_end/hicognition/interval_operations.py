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
    starts = ((regions["pos"] - window_size)//binsize) * binsize
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
