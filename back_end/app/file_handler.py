"""
TODO docstring
"""

from http.client import HTTPException
import os
import logging
from flask import current_app
from matplotlib.pyplot import switch_backend
from werkzeug.utils import secure_filename
import pandas as pd
import requests
import re
import gzip
from hicognition import io_helpers
from . import create_app, db
from .models import Assembly, Dataset, IndividualIntervalData, Collection, User, DataRepository, User_DataRepository_Credentials
from . import pipeline_steps, file_handler
from .notifications import NotificationHandler


# get logger
log = logging.getLogger("rq.worker")

# setup app context

app = create_app(os.getenv("FLASK_CONFIG") or "default")
app.app_context().push()

# set up notification handler

notifcation_handler = NotificationHandler()

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

    
def save_file(file_path: str, content, overwrite=False):
    """saves a file to file_path"""
    if not overwrite and os.path.exists(file_path):
        raise FileExistsError(f'File at {file_path} already exists and overwrite is {overwrite}')
    
    with open(file_path, 'wb') as f_out:
        f_out.write(content)
