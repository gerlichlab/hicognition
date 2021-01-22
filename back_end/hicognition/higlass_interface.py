"""Functions to interface with Higlass."""
import subprocess
import shlex
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
import json

# define Clodius templates
CLODIUS_TEMPLATES = {
    "bedfile": "clodius aggregate bedfile --chromsizes-filename {} -o {} {}",
    "bedpe": "clodius aggregate bedpe --chromsizes-filename {}\
                                      --chr1-col 1 --from1-col 2 --to1-col 3 \
                                      --chr2-col 4 --from2-col 5 --to2-col 6 \
                                      --output-file {} {}",
}

# define filetype and datatype mapping for upload

DATATYPES = {
    "bedfile": "bedlike",
    "bedpe": "2d-rectangle-domains",
    "cooler": "matrix",
    "bigwig": "vector",
}

FILETYPE = {
    "bedfile": "beddb",
    "cooler": "cooler",
    "bedpe": "bed2ddb",
    "bigwig": "bigwig"
}


def add_tileset(file_type, file_path, higlass_url, credentials, name):
    """Adds tileset to a Higlass server.

    returns uuid of new tileset or raises error if unsuccessful.
    """
    # Stitch together request
    files = {"datafile": open(file_path, "rb")}
    data = {
        "filetype": FILETYPE[file_type],
        "datatype": DATATYPES[file_type],
        "coordSystem": "hg19",
        "name": name,
    }
    # dispatch request
    request = requests.post(
        url=higlass_url, files=files, data=data, auth=HTTPBasicAuth(credentials["user"], credentials["password"])
    )
    # check whether return code was okay
    if request.status_code != 201:
        raise HTTPError("Upload did not succeed!")
    return json.loads(request.text)


def preprocess_dataset(file_type, chromsizes_path, file_path, output_path):
    """Preprocess file using clodius.

    Function returns the exit code of
    the conversion subprocess, because it only
    has a side-effect."""
    # get correct command template
    command_template = CLODIUS_TEMPLATES.get(file_type, None)
    if command_template is None:
        raise ValueError(
            "File-type not recognized. Must be either 'bedfile' or 'bedpe'! "
        )
    # fill in command
    command = command_template.format(chromsizes_path, output_path, file_path)
    # dispatch command
    process = subprocess.run(shlex.split(command), check=False, capture_output=True)
    # return exit code
    if len(process.stderr) != 0: # some errors are considered "input errors" and don't change exit code
        return 1
    return process.returncode
