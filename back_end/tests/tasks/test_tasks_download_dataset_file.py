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
        
        # # make datasets for these test cases:
        # self.dataset_repo = Dataset(
        #     dataset_name="ds",
        #     filetype="bedfile",
        #     processing_state='uploading',
        #     user_id=1,
        #     assembly=1,
        #     sizeType="Point",
        #     repository_name = '4DN',
        #     sample_id = '4DNFIRCHWS8M'
        # )
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
        self.dataset_valid_not_exists_url = Dataset(
            dataset_name="ds",
            filetype="bedfile",
            processing_state='uploading',
            user_id=1,
            assembly=1,
            sizeType="Point",
            source_url='https://this42url1337isgoinnowhere.at'
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
        # db.session.add(self.dataset_repo)
        db.session.add(self.dataset_bad_id_4dn)
        db.session.add(self.dataset_bed_gz)
        db.session.add(self.dataset_bad_url)
        db.session.add(self.dataset_valid_not_exists_url)
        db.session.add(self.dataset_url)
        db.session.add(self.repo1)
        db.session.commit()
        
        
    # @patch('app.api.get_routes.get_ENCODE_metadata')
    # @patch('app.download_utils.download_file') # TODO test this
    # def test_download_wo_authentication(self, mock_encode_metadata, mock_json_content):
    #     mock_encode_metadata = str({
    #         'status': 'ok',
    #         'json': {
    #             'open_data_url': 'thisisurl',
    #             'href': 'thisisurl',
    #             'md5sum': '0934773585cd8b75960444d97cc3d41e',
    #             'display_title': '4DNFIRCHWS8M.bed.gz'
    #         }
    #     })
    #     file_name = '4DNFIRCHWS8M.bed.gz'
    #     with open(os.path.join(TempDirTestCase.TEMP_PATH, '4DNFIRCHWS8M.bed.gz'), 'rb') as bedgz_file:
    #         content = bedgz_file.read()
    #     mock_json_content = (file_name, content)
    #     http_status = download_dataset_file(self.dataset_no_auth.id, TempDirTestCase.TEMP_PATH)
        
    #     self.assertEqual(True, http_status)
    #     # TODO check file content

    
    # def test_download_url_not_valid(self): # TODO throws no exceptions, check for notification and deleted
    #     with self.assertRaises(requests.exceptions.MissingSchema):
    #         download_dataset_file(
    #             self.dataset_bad_url.id,
    #             TempDirTestCase.TEMP_PATH
            # )
    # def test_download_url_valid_but_not_real(self): # TODO throws no exceptions, check for notification and deleted
    #     with self.assertRaises(requests.exceptions.ConnectionError):
    #         download_dataset_file(
    #             self.dataset_valid_not_exists_url.id,
    #             TempDirTestCase.TEMP_PATH
    #         )

    # def test_download_id_not_valid(self): # TODO throws no exceptions, check for notification and deleted
    #     http_status = download_dataset_file(self.dataset_bad_id_4dn.id, TempDirTestCase.TEMP_PATH)
    #     self.assertEqual(200, http_status)
    
    # def test_download_dataset_not_found(self):
    #     download_dataset_file(1000, TempDirTestCase.TEMP_PATH)
    #     self.assertRaises()


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
