"""Collection of format checkers for biological data formats. """
import os
import re
import cooler
import logging

from .io_helpers import clean_bedpe, clean_bed

def is_region_file_correctly_formatted(file_path, chromosome_names, _):
    if file_path.lower().endswith('bed'):
        return is_bed_file_correctly_formatted(file_path, chromosome_names, _)
    elif file_path.lower().endswith('bedpe'):
        return is_bedpe_file_correctly_formatted(file_path, chromosome_names, _)
    else:
        logging.warning(f'File {file_path} was handed to format checker as region?')
        return False

def is_bedpe_file_correctly_formatted(file_path, chromosome_names, _):
    try:
        clean_bedpe(file_path, os.devnull, chromosome_names)
    except (ValueError, KeyError, BaseException) as err:
        logging.warning(f'bedpe file was not valid: {err}')
        return False
    return True

def is_bed_file_correctly_formatted(file_path, chromosome_names, _):
    try:
        clean_bed(file_path, os.devnull, chromosome_names)
    except (ValueError, KeyError, BaseException) as err:
        logging.warning(f'bed file was not valid: {err}')
        return False
    return True


def is_mcooler(file_path, chromosome_names, needed_resolutions):
    """Tests whether cooler file
    is an mcool with required resolutions."""
    try:
        resolutions = cooler.fileops.list_coolers(file_path)
        # check whether needed_resolutions are available
        for needed in needed_resolutions:
            if f"/resolutions/{needed}" not in resolutions:
                logging.warning(f"resolution {needed} not in cooler!")
    except BaseException:
        return False
    return True


FORMAT_CHECKERS = {
    "bedfile": is_region_file_correctly_formatted,
    "cooler": is_mcooler,
    "bigwig": lambda x, y, z: True,
    "chromsizes": lambda x: True,
    "chromarms": lambda x: True,
}
