"""Test getting genome assemblies."""
import unittest
import json
from unittest.mock import patch
from hicognition.test_helpers import LoginTestCase

# add path to import app
# import sys
# sys.path.append("./")
from app import db
from app.models import User, DataRepository, User_DataRepository_Credentials


class TestGetMetadata(LoginTestCase):
    """Test getting genome assemblies."""

    def setUp(self):
        super().setUp()
        
        # testfile created from:
        # curl --user key:secret https://data.4dnucleome.org/files-processed/4DNFIRCHWS8M/ -H "Accept: application/json" > 4DNFIRCHWS8M.json

        
        #users = 1
        
        # add repos
        self.data_repo_4dn = DataRepository(name='4dn', url='https://data.4dnucleome.org/files-processed/{id}', auth_required=False)
        self.data_repo_4dn_auth = DataRepository(name='4dn_auth', url='https://data.4dnucleome.org/files-processed/{id}', auth_required=True)
        self.data_repo_4dn_incorrect_auth = DataRepository(name='4dn_auth_2', url='https://data.4dnucleome.org/files-processed/{id}', auth_required=True)
        
        self.credentials = User_DataRepository_Credentials(
            user_id = 1, 
            repository_name = '4dn_auth',
            key = '2SLNQIYV',
            secret = 'pwani4r7dpezvl4d' # TODO DO NOT COMMIT
        )
        self.credentials_fail = User_DataRepository_Credentials(
            user_id = 1, 
            repository_name = '4dn_auth_2', 
            key = 'key',
            secret = 'secret'
        )
        
        self.sample_valid = '4DNFIRCHWS8M'
        with open('./tests/testfiles/4DNFIRCHWS8M.json', 'r') as sample_json:
            self.sample_json_str = sample_json.read()
        self.sample_json = json.loads(self.sample_json_str)
        self.token_header = self.get_token_header(self.add_and_authenticate("test", "asdf"))
        
        db.session.add(self.data_repo_4dn)
        db.session.add(self.data_repo_4dn_auth)
        db.session.add(self.data_repo_4dn_incorrect_auth)
        db.session.add(self.credentials)
        db.session.add(self.credentials_fail)
        db.session.commit()
        

    def test_no_auth(self):
        """No authentication provided, response should be 401"""
        response = self.client.get(f"/api/ENCODE/4dn/{self.sample_valid}/", content_type="application/json")
        self.assertEqual(response.status_code, 401)


    def test_correct_sample_returned_no_auth(self):
        response = self.client.get(
            f"/api/ENCODE/4dn/{self.sample_valid}/", 
            content_type="application/json", 
            headers=self.token_header)
        rjson = json.loads(response.data.decode())
        self.assertEqual(rjson['status'], 'ok')
        self.assertEqual(rjson['json'], self.sample_json)
        

    def test_sample_not_found(self):
        response = self.client.get(
            f"/api/ENCODE/4dn/TESTIDNOTFOUND/", 
            content_type="application/json",
            headers=self.token_header)
        self.assertEqual(response.status_code, 200) # ASK should i give back 404?
        rjson = json.loads(response.data.decode())
        self.assertEqual(rjson['status'], 'sample_not_found')
        
        
    def test_correct_sample_returned_auth(self):
        response = self.client.get(
            f"/api/ENCODE/4dn/{self.sample_valid}/",
            content_type="application/json",
            headers=self.token_header)
        self.assertEqual(response.status_code, 200)
        rjson = json.loads(response.data.decode())
        self.assertEqual(rjson['status'], 'ok')
        self.assertEqual(rjson['json'], self.sample_json)
        
    # def test_incorrect_credentials(self):
    #     response = self.client.get(
    #         f"/api/ENCODE/4dn_auth/{self.sample_valid}/",
    #         content_type="application/json",
    #         headers=self.token_header)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn('failed! API keys may not be correct', response.data.decode())
        
        
    


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
