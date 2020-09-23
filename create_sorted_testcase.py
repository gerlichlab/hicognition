import pandas as pd
from functools import partial

###### small testcase

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

####### small testcase with weird chromosomes

weirdChromos = pd.DataFrame({0: ["chrX", "chrY", "chrX", "chrX"], 1: [1, 2, 1, 2]})

inputFile = pd.concat((dataUnsorted, weirdChromos))
inputFile.to_csv("./tests/testfiles/test_small_weird_chromos.bed", sep="\t", index=False, header=None)

# correct result

inputFile.index = range(len(inputFile))
dummyIndex = inputFile.index

sortedByGenomicPos = inputFile.sort_values(by=[1])

sortedIndex = sorted(dummyIndex, key=partial(sortFunction, dataUnsorted=sortedByGenomicPos, chromsizes=chrom_order))

dataSorted = sortedByGenomicPos.iloc[sortedIndex, :]

dataSorted.to_csv("./tests/testfiles/test_small_weird_chromos_sorted.bed", sep="\t", index=False, header=None)

###### small testcase with chromosomes that are not in our chromsize

badChromos = pd.DataFrame({0: ["chrB", "chrA", "chrD"], 1: [1, 2, 3]})

inputFile = pd.concat((dataUnsorted, badChromos))
inputFile.to_csv("./tests/testfiles/test_small_bad_chromos.bed", sep="\t", index=False, header=None)

# expected behavior, remove the bad chromosoes, smae as test_small_sorted.bed