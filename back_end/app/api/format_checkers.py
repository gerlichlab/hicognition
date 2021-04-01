import pandas as pd
import cooler


def is_bed_file_correctly_formatted(file_path):
    """Takes file and checks
    whether reading results in a correct bedfile."""
    try:
        bed_frame = pd.read_csv(file_path, sep="\t", header=None, comment="#")
    except:
        return False
    return True


def is_mcooler(file_path):
    """Tests whether cooler file
    is an mcool file ty listing resolutions and trying to open them"""
    try:
        resolutions = cooler.fileops.list_coolers(file_path)
        for resolution in resolutions:
            temp_cool = cooler.Cooler(f"{file_path}::{resolution}")
    except:
        return False
    return True


FORMAT_CHECKERS = {
    "bedfile": is_bed_file_correctly_formatted,
    "cooler": is_mcooler,
    "bigwig": lambda x: True,
}
