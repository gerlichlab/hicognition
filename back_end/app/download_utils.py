"""
TODO docstring
"""

import os
import logging
from itsdangerous import json
from werkzeug.utils import secure_filename
import pandas as pd
import requests
from requests import HTTPError, RequestException
import re
import hashlib
import gzip
from . import db
from .models import (
    DataRepository,
    Dataset
)


# get logger
log = logging.getLogger("rq.worker")

# set basedir

basedir = os.path.abspath(os.path.dirname(__file__)) # TODO test me

class FileImportError(Exception): pass
class MD5Error(FileImportError): pass
class FileEmptyError(FileImportError): pass
class MetadataFetchError(FileImportError): pass
class MetadataError(FileImportError): pass

def download_file(url: str, md5checksum: str = None, gunzip_if_compressed: bool = True):
    """
    """
    response = requests.get(url, stream=True)
    response.raise_for_status()

    if response.content is None or response.content == '':
        raise FileEmptyError("200: File was empty")
    content = response.content

    # get filename
    name_search = re.findall("filename=(.+)", response.headers.get('Content-Disposition', ''))
    if len(name_search) > 0:
        filename = name_search[0].split(';')[0]
    else:
        filename = None

    # check md5sum
    if md5checksum is not None and hashlib.md5(content).hexdigest() != md5checksum:
        raise MD5Error(f'md5 hashes not equal: [{hashlib.md5(content).hexdigest()} != {md5checksum}]') 

    # check if compressed and decompress
    if gunzip_if_compressed and _is_gzipped(content):
        content = gzip.decompress(content)
        if filename and filename.lower().endswith('.gz'):
            filename = filename[:-3]

    return content, filename


def download_ENCODE_metadata(url, auth: tuple = None) -> dict: # FIXME this is bad -> exception handling should be done on a higher level.
    metadata = requests.get(url, headers={'Accept': 'application/json'}, auth=auth)
    metadata.raise_for_status()
    
    metadata_json = json.loads(metadata.content)
    return metadata_json

# https://stackoverflow.com/questions/3703276/how-to-tell-if-a-file-is-gzip-compressed
def _is_gzipped(file_content):
    """checks if a byte array is gzipped by checking the gzip magic numbers
    """
    return file_content[:2] == b'\x1f\x8b' # Gzip magic numbers

    
def download_encode(ds: Dataset, upload_dir: str, _: str = None):
    """ """
    log.info(f'Getting metadata for {ds.id} from {ds.repository_name}')
    try:
        metadata = download_ENCODE_metadata(ds.repository_name, ds.sample_id)
    except RequestException as err:
        log.info(f'Dataset {ds.id}: metadata could not be retrieved')
        raise MetadataFetchError('Metadata Fetch error: %s' % str(err))
 
    # elif metadata.get('href'):
    #     ds.source_url = metadata['href'] # TODO make way to attach href to the repo url
    ds.source_url = metadata.get('open_data_url')
    if not ds.source_url:
        log.info(f'Dataset {ds.id}: metadata json missing source url')
        raise MetadataError('No source URL could be found for sample id %s' % ds.sample_id)
    
    # download file
    http_content, http_file_name = download_file(
        url=ds.source_url,
        md5=metadata.get('md5sum', None),
        gunzip_if_compressed=True
    )
    file_name = secure_filename(f"{ds.id}_{metadata.get('display_title', http_file_name)}") # contains file_name with ext
    file_name = file_name[:-3] if file_name.lower().endswith('.gz') else file_name
    
            
    # save file
    ds.file_path = os.path.join(upload_dir, secure_filename(file_name))
    if os.path.exists(ds.file_path):
        log.info(f'Datset {ds.id}: File at {ds.file_path} already exists')
        raise IOError(f'File at {ds.file_path} already exists')
    with open(ds.file_path, 'w') as f_out:
        f_out.write(http_content.decode())
        
    ds.processing_state = "uploaded"
    return ds

def download_url(ds: Dataset, upload_dir: str, file_ext: str, md5sum: str = None):
    """Downloads from URL; chooses a file_name, depending on headers;
    gunzips if the data is gzipped; saves to upload_dir/name;
    changes dataset.processing_state to 'uploaded'

    Args:
        ds (Dataset): Dataset containing a valid source_url
        upload_dir (str): where to place file after gunzipping
        file_ext (str): extension of the file that will be saved
        
    Exceptions:
        HTTPError 404, 403, 400 or similar if URL is wrong
        IOException if file already exists
    """
    http_content, http_file_name = download_file(ds.source_url, md5sum, gunzip_if_compressed=True)
    if http_file_name:
        file_name = f'{ds.id}_{http_file_name}'
    else:
        file_name = f'{ds.id}_{ds.dataset_name}.{file_ext}'
    if file_name.lower().endswith('.gz'):
        file_name = file_name[:-3]
    
    # save file
    ds.file_path = os.path.join(upload_dir, secure_filename(file_name))
    if os.path.exists(ds.file_path):
        log.info(f'File at {ds.file_path} already exists')
        raise IOError(f'File at {ds.file_path} already exists')
    with open(ds.file_path, 'w') as f_out:
        f_out.write(http_content.decode())
    ds.processing_state = "uploaded"
    
    return ds
    