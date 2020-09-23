import pandas as pd
from functools import partial

dataUnsorted = pd.read_csv("./tests/testfiles/test_small.bed", sep="\t", header=None)
chromsizes = pd.read_csv("./data/hg19.chrom.sizes", sep="\t", header=None)
chrom_order = chromsizes[0].to_list()

def sortFunction(element, dataUnsorted, chromsizes):
    return chromsizes.index(dataUnsorted.iloc[element, 0])


dummyIndex = dataUnsorted.index

sortedByGenomicPos = dataUnsorted.sort_values(by=[1])

sortedIndex = sorted(dummyIndex, key=partial(sortFunction, dataUnsorted=sortedByGenomicPos, chromsizes=chrom_order))

dataSorted = sortedByGenomicPos.iloc[sortedIndex, :]


dataSorted.to_csv("./tests/testfiles/test_small_sorted.bed", sep="\t", index=False, header=None)