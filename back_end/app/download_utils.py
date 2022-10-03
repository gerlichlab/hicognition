"""File containing download functions for post_routes.add_dataset_from_URL,
post_routes.add_dataset_from_ENCODE and get_routes.get_ENCODE_metadata.
"""

import os
import logging
import json
from werkzeug.utils import secure_filename
import requests
from requests import RequestException
import re
import hashlib
import gzip
from . import db
from .models import Dataset


# get logger
log = logging.getLogger("rq.worker")

# set basedir

basedir = os.path.abspath(os.path.dirname(__file__))  # TODO test me


class FileImportError(Exception):
    pass


class MD5Error(FileImportError):
    pass


class FileEmptyError(FileImportError):
    pass


class NoFileNameFoundError(FileImportError):
    pass


class MetadataFetchError(FileImportError):
    pass


class MetadataError(FileImportError):
    pass


class FiletypeNotSupportedError(FileImportError):
    pass


def download_file(url: str, md5sum: str = None, decompress: bool = True) -> bytearray:
    """Downloads a file into memory and checks md5sum if provided, and also
    decompresses it if it is gzip compressed.


    Args:
        url (str): URL to file
        md5sum (str, optional): Defaults to None.
        decompress (bool, optional): If true checks file whether it is compressed using
            gzip and then decompresses. Defaults to True.

    Raises:
        FileEmptyError: Raised if file is empty
        MD5Error: Raised if MD5 checksum is not correct

    Returns:
        bytearray: Returns file as byte array
    """
    log.info(f"Downloading {url}")
    # response = requests.get(url, stream=True)
    response = requests.get(url, stream=True)
    log.info(f"done.")
    response.raise_for_status()

    if response.content is None or response.content == "":
        raise FileEmptyError("200: File was empty")
    content = response.content

    # get filename
    name_search = re.findall(
        "filename=(.+)", response.headers.get("Content-Disposition", "")
    )
    if len(name_search) > 0:
        filename = name_search[0].split(";")[0]
    else:
        filename = None

    # check md5sum
    if md5sum is not None and hashlib.md5(content).hexdigest() != md5sum:
        raise MD5Error(
            f"md5 hashes not equal: [{hashlib.md5(content).hexdigest()} != {md5sum}]"
        )

    # check if compressed and decompress
    if decompress and _is_gzipped(content):
        content = gzip.decompress(content)
        if filename and filename.lower().endswith(".gz"):
            filename = filename[:-3]

    return content, filename


def download_ENCODE_metadata(url: str, auth: tuple = None) -> dict:
    """Gets metadata from an ENCODE repository with a provided URL.

    Args:
        url (str): URL to the json file
        auth (tuple, optional): Authentication can be provided if needed. Defaults to None.

    Returns:
        dict: Returns metadata in form of ENCODE (see https://www.encodeproject.org/profiles/)
    """
    metadata = requests.get(url, headers={"Accept": "application/json"}, auth=auth)
    metadata.raise_for_status()
    metadata_json = json.loads(metadata.content)
    return metadata_json


# https://stackoverflow.com/questions/3703276/how-to-tell-if-a-file-is-gzip-compressed
def _is_gzipped(file_content: bytearray):
    """checks if a byte array is gzipped by checking the gzip magic numbers"""
    return file_content[:2] == b"\x1f\x8b"  # Gzip magic numbers


def download_encode(ds: Dataset, upload_dir: str):
    """Adds url to file to a dataset, using ENCODE metadata.
    Then downloads the file and checks for validity.
    Updated dataset has to be commited to db by function invoker.

    Args:
        ds (Dataset): Dataset which must have sample id and repository name set
        upload_dir (str): Directory to store file in

    Raises:
        MetadataFetchError: Metadata could not be downloaded.
        MetadataError: Metadata not in the expected form
        FiletypeNotSupportedError: FileType different than expected
        NoFileNameFoundError: no file name could not be determined
        IOError: Raised if there are problems saving the file

    Returns:
        Datset: dataset is returned, not yet commited
    """
    # log.info(f"Dataset [{ds.id}]: Getting metadata for sample '{ds.sample_id}' from {ds.repository_name}")
    try:
        metadata = download_ENCODE_metadata(ds.repository.build_url(ds.sample_id))
    except RequestException as err:
        log.info(f"Dataset [{ds.id}]: metadata could not be retrieved")
        raise MetadataFetchError(f"Metadata Fetch error:{str(err)}")

    # elif metadata.get('href'):
    #     ds.source_url = metadata['href'] # TODO make way to attach href to the repo url
    ds.source_url = metadata.get("open_data_url")
    if not ds.source_url:
        log.info(f"Dataset [{ds.id}]: metadata json missing source url")
        raise MetadataError(
            f"No source URL could be found for sample id {ds.sample_id}"
        )

    # forbid mcool for now (sept2022)
    if metadata.get("file_format", {}).get("file_format", "").lower() in [
        "mcool",
        "cool",
    ]:
        raise FiletypeNotSupportedError(
            "External import of cooler files not supported yet."
        )

    # download file
    # log.info(f"Dataset [{ds.id}]: Downloading from {ds.source_url}.")
    download_tuple = download_file(
        url=ds.source_url,
        md5sum=metadata.get("md5sum", None),
        decompress=True,
    )
    http_content = download_tuple[0]
    http_file_name = download_tuple[1]
    # log.info(f"Dataset [{ds.id}]: saved to memory.")

    file_name = metadata.get("display_title", http_file_name)
    if not file_name:
        raise NoFileNameFoundError("For Dataset {ds.id} no file name was found.")
    if file_name.lower().endswith("gz"):
        file_name = file_name[:-3]
    file_name = f"{ds.id}_{file_name}"
    ds.file_path = os.path.join(upload_dir, secure_filename(file_name))

    # save file
    # log.info(f"Dataset [{ds.id}]: saving to file {ds.file_path}")
    if os.path.exists(ds.file_path):
        log.info(f"Dataset [{ds.id}]: File at {ds.file_path} already exists")
        raise IOError(f"File already exists")
    with open(ds.file_path, "wb") as f_out:
        f_out.write(http_content)

    # log.info(f"Dataset [{ds.id}]: saved.")
    ds.processing_state = "uploaded"
    return ds


def download_url(ds: Dataset, upload_dir: str, file_ext: str, md5sum: str = None):
    """Downloads from URL; chooses a file_name, depending on headers.
    Gunzips if the data is gzipped.
    Saves to upload_dir/name.
    Changes dataset.processing_state to 'uploaded'

    Args:
        ds (Dataset): Dataset containing a valid source_url
        upload_dir (str): where to place file after gunzipping
        file_ext (str): extension of the file that will be saved

    Exceptions:
        FiletypeNotSupportedError: FileType different than expected
        IOError: Raised if there are problems saving the file
        HTTPError: requests module raises those if there are problems with URL

    Returns:
        Datset: dataset is returned, not yet commited
    """

    # forbid mcool for now (sept2022)
    if file_ext.lower() in ["mcool", "cool"]:
        raise FiletypeNotSupportedError(
            "External import of cooler files not supported yet."
        )

    (http_content, http_file_name) = download_file(
        ds.source_url, md5sum, decompress=True
    )
    if http_file_name:
        file_name = f"{ds.id}_{http_file_name}"
    else:
        file_name = f"{ds.id}_{ds.dataset_name}.{file_ext}"
    if file_name.lower().endswith(".gz"):
        file_name = file_name[:-3]

    # save file
    ds.file_path = os.path.join(upload_dir, secure_filename(file_name))
    if os.path.exists(ds.file_path):
        log.info(f"File at {ds.file_path} already exists")
        raise IOError(f"File at {ds.file_path} already exists")
    with open(ds.file_path, "wb") as f_out:
        f_out.write(http_content)
    ds.processing_state = "uploaded"

    return ds
