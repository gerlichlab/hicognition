from hicognition.format_checkers import is_bed_file_correctly_formatted, is_mcooler


FORMAT_CHECKERS = {
    "bedfile": is_bed_file_correctly_formatted,
    "cooler": is_mcooler,
    "bigwig": lambda x, y: True,
}
