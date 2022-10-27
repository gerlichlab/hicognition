"""File containing download functions for post_routes.add_dataset_from_URL,
post_routes.add_dataset_from_ENCODE and get_routes.get_ENCODE_metadata.
"""

import os
import logging
import json
import re
import hashlib
import gzip
from werkzeug.utils import secure_filename
import requests
from .models import Dataset, Repository


# get logger
log = logging.getLogger("rq.worker")

# set basedir

basedir = os.path.abspath(os.path.dirname(__file__))  # TODO test me


class DownloadUtilsException(Exception):
    """General exception to be thrown if download fails"""


class MD5Exception(DownloadUtilsException):
    """MD5 checksums do not match"""


class FileEmptyException(DownloadUtilsException):
    """Downloaded file is empty"""


class MetadataNotWellformed(DownloadUtilsException):
    """Metadata is missing some needed fields"""


class FiletypeNotSupportedException(DownloadUtilsException):
    """Temporarily blocks cooler files until we have implemented reprocessing of it"""


class FileExistsException(DownloadUtilsException):
    """There already is a file at the path"""


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
    response = requests.get(url, stream=True, timeout=5)
    response.raise_for_status()
    if response.content is None or response.content == "":
        raise FileEmptyException("200: File was empty")
    content = response.content
    log.info("loaded into memory.")

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
        raise MD5Exception(
            f"md5 hashes not equal: [{hashlib.md5(content).hexdigest()} != {md5sum}]"
        )

    # check if compressed and decompress
    if decompress and _is_gzipped(content):
        content = gzip.decompress(content)
        if filename and filename.lower().endswith(".gz"):
            filename = filename[:-3]

    return content, filename


def download_ENCODE_metadata(
    repository: Repository, sample_id: str, auth: tuple = None
) -> dict:
    """Gets metadata from an ENCODE repository with a provided URL.

    Args:
        repository (Repository): repository to contact
        sample_id (str): sample id provided
        auth (tuple, optional): needed if authentication is required. Defaults to None.

    Raises:
        MetadataNotWellformed: metadata is empty or missing fields

    Returns:
        dict: Returns metadata in form of ENCODE (see https://www.encodeproject.org/profiles/)
    """
    metadata_url = repository.build_url_sample(sample_id)
    metadata = requests.get(
        metadata_url, headers={"Accept": "application/json"}, auth=auth, timeout=5
    )
    metadata.raise_for_status()

    if not metadata or metadata == {}:
        raise MetadataNotWellformed("Returned metadata was empty")

    try:
        metadata = json.loads(metadata.content)
    except Exception as err:
        raise MetadataNotWellformed(
            "Could not transform returned metadata to json"
        ) from err
    if not (metadata.get("open_data_url") or metadata.get("href")):
        raise MetadataNotWellformed(f"No source URL in metadata of {sample_id}.")
    if not metadata.get("file_format") or not metadata["file_format"].get(
        "file_format"
    ):
        raise MetadataNotWellformed(
            f"No file type specified in metadata of {sample_id}."
        )
    if not metadata.get("display_title"):
        raise MetadataNotWellformed(f"For {sample_id} no file name was found.")

    return metadata


# https://stackoverflow.com/questions/3703276/how-to-tell-if-a-file-is-gzip-compressed
def _is_gzipped(file_content: bytearray):
    """checks if a byte array is gzipped by checking the gzip magic numbers"""
    return file_content[:2] == b"\x1f\x8b"  # Gzip magic numbers


def download_encode(dataset: Dataset, upload_dir: str):
    """Adds url to file to a dataset, using ENCODE metadata.
    Then downloads the file and checks for validity.
    Updated dataset has to be commited to db by function invoker.

    Args:
        ds (Dataset): Dataset which must have sample id and repository name set
        upload_dir (str): Directory to store file in

    Raises:
        FiletypeNotSupportedError: FileType different than expected
        FileExistsException: Raised if there are problems saving the file

    Returns:
        Datset: dataset is returned, not yet commited
    """
    # log.info(f"Dataset [{ds.id}]: Getting metadata for sample
    #   '{ds.sample_id}' from {ds.repository_name}")
    metadata = download_ENCODE_metadata(dataset.repository, dataset.sample_id)

    dataset.source_url = metadata.get("open_data_url")
    if not dataset.source_url:
        dataset.source_url = dataset.repository.build_url(metadata.get("href"))

    # forbid mcool for now (sept2022)
    if metadata["file_format"]["file_format"].lower() in [
        "mcool",
        "cool",
    ]:
        raise FiletypeNotSupportedException(
            "External import of cooler files not supported yet."
        )

    # download file to memory and get name
    download_tuple = download_file(
        url=dataset.source_url,
        md5sum=metadata.get("md5sum", None),
        decompress=True,
    )
    http_content = download_tuple[0]
    http_file_name = download_tuple[1]

    # prepare file path to save file to. take name from metadata if not retrieved in http request
    file_name = metadata.get("display_title", http_file_name)
    if file_name.lower().endswith("gz"):
        file_name = file_name[:-3]
    file_name = f"{dataset.id}_{file_name}"
    dataset.file_path = os.path.join(upload_dir, secure_filename(file_name))

    # save file
    if os.path.exists(dataset.file_path):
        log.info(f"Dataset [{dataset.id}]: File at {dataset.file_path} already exists")
        raise FileExistsException(f"File {file_name} already exists in file system.")
    with open(dataset.file_path, "wb") as f_out:
        f_out.write(http_content)

    dataset.processing_state = "uploaded"
    return dataset


def download_url(dataset: Dataset, upload_dir: str, file_ext: str, md5sum: str = None):
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
        FileExistsException: Raised if there are problems saving the file

    Returns:
        Datset: dataset is returned, not yet commited
    """

    # forbid mcool for now (sept2022)
    if file_ext.lower() in ["mcool", "cool"]:
        raise FiletypeNotSupportedException(
            "External import of cooler files not supported yet."
        )

    (http_content, http_file_name) = download_file(
        dataset.source_url, md5sum, decompress=True
    )
    if http_file_name:
        file_name = f"{dataset.id}_{http_file_name}"
    else:
        file_name = f"{dataset.id}_{dataset.dataset_name}.{file_ext}"
    if file_name.lower().endswith(".gz"):
        file_name = file_name[:-3]

    # save file
    dataset.file_path = os.path.join(upload_dir, secure_filename(file_name))
    if os.path.exists(dataset.file_path):
        log.info(f"Dataset [{dataset.id}]: File at {dataset.file_path} already exists")
        raise FileExistsException(f"File {file_name} already exists in file system.")
    with open(dataset.file_path, "wb") as f_out:
        f_out.write(http_content)

    dataset.processing_state = "uploaded"
    return dataset
