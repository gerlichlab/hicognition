"""Module with the tests for the stackup creation realted tasks."""
import unittest
from unittest.mock import patch
import pandas as pd
import numpy as np
from hicognition.test_helpers import LoginTestCase, TempDirTestCase
from hicognition import interval_operations

from app.tasks import download_dataset_file

# add path to import app
# import sys
# sys.path.append("./")
from app import db
from app.models import *
from app.pipeline_steps import stackup_pipeline_step

from app.pipeline_worker_functions import (
    _do_stackup_fixed_size,
    _do_stackup_variable_size,
)

import requests


class TestDownloadDatasetFile(LoginTestCase, TempDirTestCase):
    """Tests for pipeline stackup"""

    def setUp(self):
        # TODO setUp runs twice?!

        super(TestDownloadDatasetFile, self).setUp()
        # add assembly
        self.hg19 = Assembly(
            id=1,
            name="hg19",
            chrom_sizes=self.app.config["CHROM_SIZES"],
            chrom_arms=self.app.config["CHROM_ARMS"],
        )
        db.session.add(self.hg19)
        db.session.commit()
        # make users
        # user1 exists already
        
        self.user = User(id=1, username='user1')
        self.user.set_password('pass1')

        # make repos
        # repo1: empty repo (takes urls)
        self.repo1 = DataRepository( # do we even need that? if no repo specified use none
            id = 1,
            name = "4DN",
            url = "https://data.4dnucleome.org/files-processed/{id}/@@download", # TODO bed gz evil
            auth_required = True
        )
        # repo2: 4dn repo (takes url/id)
        
        # make repo_user_credentials
        # user1_4dn
        self.user1_4dn_cred = User_DataRepository_Credentials(
            user_id = 1,
            repository_id = 1,
            key='23MPZ4TF',
            secret='exa7hrtx53tjmusq' # TODO remove before upload?!
        )
        
        # make datasets for these test cases:
        self.dataset = Dataset(
            dataset_name="ds",
            file_path=os.path.join(TempDirTestCase.TEMP_PATH, "/test_bed.bed"),
            filetype="bedfile",
            processing_state='uploading',
            user_id=1,
            assembly=1,
            sizeType="Point",
            repo_id = 1,
            repo_file_id = '4DNFIRCHWS8M'
        )
        self.dataset_no_auth = Dataset(
            dataset_name="ds",
            file_path='',
            filetype="bedfile",
            processing_state='uploading',
            user_id=1,
            assembly=1,
            sizeType="Point",
            source_url='https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSE202471&format=file&file=GSE202471_MergeRetina2_Domain_Call_TADs_10kb%2Ebed%2Egz'
        )
        self.dataset_missing_auth = Dataset(
            dataset_name="ds",
            file_path='',
            filetype="bedfile",
            processing_state='uploading',
            user_id=1,
            assembly=1,
            sizeType="Point",
            source_url='https://data.4dnucleome.org/files-processed/4DNFIRCHWS8M/@@download'
        )
        self.dataset_bed_gz = Dataset(
            dataset_name="ds",
            file_path='',
            filetype="bedfile",
            processing_state='uploading',
            user_id=1,
            assembly=1,
            sizeType="Point",
            source_url='https://data.4dnucleome.org/files-processed/4DNFIRCHWS8M/@@download'
        )
        self.dataset_bad_url = Dataset(
            dataset_name="ds",
            file_path='',
            filetype="bedfile",
            processing_state='uploading',
            user_id=1,
            assembly=1,
            sizeType="Point",
            source_url='https://this.is.a.bad.url'
        )        
        self.dataset_bad_id_4dn = Dataset(
            dataset_name="ds",
            file_path='',
            filetype="bedfile",
            processing_state='uploading',
            user_id=1,
            assembly=1,
            sizeType="Point",
            repo_id=1,
            repo_file_id="THISISNOTANID"
        )

        db.session.add(self.user)
        db.session.add(self.dataset)
        db.session.add(self.dataset_no_auth)
        db.session.add(self.dataset_bad_id_4dn)
        db.session.add(self.dataset_bed_gz)
        db.session.add(self.dataset_bad_url)
        db.session.add(self.dataset_missing_auth)
        db.session.add(self.user1_4dn_cred)
        db.session.add(self.repo1)
        db.session.commit()
        
        # dataset w/o authentication needed 
        # dataset w/ authentication needed from 4dn
        # dataset w/ authentication needed from 4dn, auth fail
        # dataset w/ malformed bed file
        # dataset w/ malformed mcooler file
        # dataset w/ malformed cooler file
        # dataset w/ malformed bigwig file
        # dataset w/ wrong url/id
        # dataset w/ no internet connection (e.g. if server is in intranet)
        
    # TODO learn when to use patch @ decorator
    # TODO test_helpers.py should remove tmp_test if exists


    def test_download_wo_authentication(self):
        http_status = download_dataset_file(self.dataset_no_auth.id, TempDirTestCase.TEMP_PATH, 'bed.gz')
        
        self.assertEqual(200, http_status)
        # TODO check file content

    def test_download_missing_authentication(self):
        http_status = download_dataset_file(self.dataset_missing_auth.id, TempDirTestCase.TEMP_PATH, 'bed.gz')
        
        self.assertEqual(403, http_status)

    def test_download_w_authentication(self):
        http_status = download_dataset_file(self.dataset.id, TempDirTestCase.TEMP_PATH, 'bed.gz')
        
        self.assertEqual(200, http_status)
        # TODO check file content

    
    def test_download_url_not_valid(self):
        with self.assertRaises(requests.exceptions.ConnectionError):
            download_dataset_file(
                self.dataset_bad_url.id,
                TempDirTestCase.TEMP_PATH,
                'bed.gz'
            )

    def test_download_id_not_valid(self):
        http_status = download_dataset_file(self.dataset_bad_id_4dn.id, TempDirTestCase.TEMP_PATH, 'bed.gz')
        self.assertEqual(404, http_status) # TODO bad


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
