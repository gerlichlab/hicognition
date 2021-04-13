"""Collection of format checkers for biological data formats. """
import pandas as pd
import re
import cooler


def is_bed_file_correctly_formatted(file_path, chromosome_names):
    """Takes bed-file and checks whether it is correctly formated"""
    try:
        # first, read in the file
        with open(file_path, "r") as f:
            content = f.read()
            lines = content.split("\n")
        # strip comment header
        skipped_rows = 0
        for line in lines:
            if (line[0] == "#") or (line[:5] == "track") or (line[:7] == "browser"):
                skipped_rows += 1
                continue
            break
        # check whether next line contains column names -> first three columns will contain chrSomething number number
        potential_header_line = lines[skipped_rows]
        split_header = potential_header_line.split("\t")
        if not _is_bed_row(split_header):
            # first row is header
            skipped_rows += 1
        stripped_lines = lines[skipped_rows:]
        for line in stripped_lines:
            if line == "":
                continue
            if not _is_bed_row(line.split("\t")):
                return False
            # check whether chromosome part of line is in accepted chromosomes
            chrom = line.split("\t")[0]
            if chrom not in chromosome_names:
                return False
        return True
    except BaseException:
        return False


def _is_bed_row(bed_row):
    """Checks the format of a row of a bedfile.
    The logic is to check the first three fields that should be
    chromosome start end."""
    if len(bed_row) < 3:
        return False
    return (
        (re.match(r"^chr.+$", bed_row[0]) is not None)
        and (re.match(r"^[0-9]+$", bed_row[1]) is not None)
        and (re.match(r"^[0-9]+$", bed_row[2]) is not None)
    )


def is_mcooler(file_path, chromosome_names):
    """Tests whether cooler file
    is an mcool file ty listing resolutions and trying to open them"""
    try:
        resolutions = cooler.fileops.list_coolers(file_path)
        for resolution in resolutions:
            temp_cool = cooler.Cooler(f"{file_path}::{resolution}")
    except:
        return False
    return True