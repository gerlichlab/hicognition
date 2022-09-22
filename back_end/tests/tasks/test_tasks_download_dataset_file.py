""" """
import unittest
from unittest.mock import patch
from hicognition.test_helpers import LoginTestCase, TempDirTestCase

from app.tasks import download_dataset_file

# add path to import app
# import sys
# sys.path.append("./")
from app import db
from app.models import *

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
            name = "4DN",
            url = "https://data.4dnucleome.org/files-processed/{id}/@@download", # TODO bed gz evil
            auth_required = True
        )
        # repo2: 4dn repo (takes url/id)
        
        # make repo_user_credentials
        # user1_4dn
        # self.user1_4dn_cred = User_DataRepository_Credentials(
        #     user_id = "4DN",
        #     repository_id = 1,
        #     key='23MPZ4TF',
        #     secret='exa7hrtx53tjmusq' # TODO remove before upload?!
        # )
        
        # make datasets for these test cases:
        self.dataset_repo = Dataset(
            dataset_name="ds",
            filetype="bedfile",
            processing_state='uploading',
            user_id=1,
            assembly=1,
            sizeType="Point",
            repository_name = '4DN',
            sample_id = '4DNFIRCHWS8M'
        )
        self.dataset_url = Dataset(
            dataset_name="ds",
            filetype="bedfile",
            processing_state='uploading',
            user_id=1,
            assembly=1,
            sizeType="Point",
            source_url='valid_url.at/bed.bed.gz'
        )
        self.dataset_bad_url = Dataset(
            dataset_name="ds",
            filetype="bedfile",
            processing_state='uploading',
            user_id=1,
            assembly=1,
            sizeType="Point",
            source_url='thisisnotaurl'
        )
        self.dataset_bed_gz = Dataset(
            dataset_name="ds",
            filetype="bedfile",
            processing_state='uploading',
            user_id=1,
            assembly=1,
            sizeType="Point",
            source_url=''
        )
        self.dataset_bad_id_4dn = Dataset(
            dataset_name="ds",
            filetype="bedfile",
            processing_state='uploading',
            user_id=1,
            assembly=1,
            sizeType="Point",
            repository_name=1,
            sample_id="THISISNOTANID"
        )

        db.session.add(self.user)
        db.session.add(self.dataset)
        db.session.add(self.dataset_bad_id_4dn)
        db.session.add(self.dataset_bed_gz)
        db.session.add(self.dataset_bad_url)
        db.session.add(self.dataset_url)
        db.session.add(self.user1_4dn_cred)
        db.session.add(self.repo1)
        db.session.commit()
        
        
    @patch('app.api.get_routes.get_ENCODE_metadata')
    @patch('app.file_handler.download_file')
    def test_download_wo_authentication(self, mock_encode_metadata, mock_json_content):
        mock_encode_metadata = str({
            'status': 'ok',
            'json': {
                'open_data_url': 'thisisurl',
                'href': 'thisisurl',
                'md5sum': '0934773585cd8b75960444d97cc3d41e',
                'display_title': '4DNFIRCHWS8M.bed.gz'
            }
        })
        file_name = '4DNFIRCHWS8M.bed.gz'
        with open('4DNFIRCHWS8M.bed.gz', 'rb') as bedgz_file:
            content = bedgz_file.read()
        mock_json_content = (file_name, content)
        http_status = download_dataset_file(self.dataset_no_auth.id, TempDirTestCase.TEMP_PATH)
        
        self.assertEqual(True, http_status)
        # TODO check file content

    def test_download_missing_authentication(self):
        http_status = download_dataset_file(self.dataset_missing_auth.id, TempDirTestCase.TEMP_PATH)
        
        self.assertEqual(403, http_status)

    def test_download_w_authentication(self):
        http_status = download_dataset_file(self.dataset.id, TempDirTestCase.TEMP_PATH)
        
        self.assertTrue(http_status) # TODO change
        # TODO check file content

    
    def test_download_url_not_valid(self):
        with self.assertRaises(requests.exceptions.ConnectionError):
            download_dataset_file(
                self.dataset_bad_url.id,
                TempDirTestCase.TEMP_PATH
            )

    def test_download_id_not_valid(self):
        http_status = download_dataset_file(self.dataset_bad_id_4dn.id, TempDirTestCase.TEMP_PATH)
        self.assertEqual(404, http_status) # TODO bad


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
