"""
TODO docstring
"""

import os
import logging
from itsdangerous import json
from werkzeug.utils import secure_filename
import pandas as pd
import requests
import re
import hashlib
import gzip
from . import db
from .models import (
    DataRepository
)


# get logger
log = logging.getLogger("rq.worker")

# set basedir

basedir = os.path.abspath(os.path.dirname(__file__)) # TODO test me

def download_file(url: str, auth: tuple = None):
    """
    Downloads file and returns content as byte array
    """
    log.info(f'      Downloading from {url}')
    response = requests.get(url, auth=auth, stream=True)

    # Raise error if one occurred
    response.raise_for_status()

    if response.content is None or response.content == '':
        raise requests.HTTPError("200: File was empty")

    if 'Content-Disposition' in response.headers.keys():
        try:
            filename = re.findall("filename=(.+)", 
                response.headers['Content-Disposition'])[0].split(';')[0]
            filename = secure_filename(filename)
        except IndexError as err:
            log.info('      File name in content-disposition header was not found.')
            filename = None
    else:
        filename = None

    log.info(f'      Response status: {response.status_code}')
    return filename, response.content


def download_ENCODE_metadata(url, auth: tuple = None):
    metadata = requests.get(url, headers={'Accept': 'application/json'}, auth=auth)
    
    if metadata.status_code == 404:
        return {"status": "error", "http_status_code": 404, "message": "sample_not_found"}
    elif metadata.status_code == 403:
        return {"status": "error", "http_status_code": 403, "message": "api_credentials_wrong"}
    elif metadata.status_code > 200:
        return {"status": "error", "http_status_code": metadata.status_code,  "message": f"HTTP Error code: {metadata.status_code}"}
        #metadata.raise_for_status() # FIXME this is bad
    
    metadata_json = json.loads(metadata.content)
    response_json = {'status': "ok", "http_status_code": 200}
    response_json['json'] = metadata_json
    return response_json