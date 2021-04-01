import pandas as pd


def is_bed_file_correctly_formatted(fileObject):
    """Takes io.ByteStream object and checks
    whether reading results in a correct bedfile.
    Will reset stream position to 0."""
    try:
            bed_frame = pd.read_csv(fileObject, sep="\t", header=None, comment="#")
    except:
            fileObject.seek(0)
            return False
    fileObject.seek(0)
    return True


FORMAT_CHECKERS = {
    "bedfile": is_bed_file_correctly_formatted,
    "cooler": lambda x: True,
    "bigwig": lambda x: True
}
    