"""Test getting genome assemblies."""
import unittest
import json
from unittest.mock import patch

import requests
from hicognition.test_helpers import LoginTestCase

# add path to import app
# import sys
# sys.path.append("./")
from app import db
from app.models import DataRepository


class TestGetMetadata(LoginTestCase):
    """Test get_route for encode metadata.
    Haven't tested whether correct stuff is returned, as this is already tested in
    test_download_functions"""

    def setUp(self):
        super().setUp()
        
        self.data_repo_4dn = DataRepository(name='4dn', url='thisisurl', auth_required=False)
        db.session.add(self.data_repo_4dn)
        db.session.commit()
        
        self.token_header = self.get_token_header(self.add_and_authenticate("test", "asdf"))

    def test_found_repository_but_url_is_wrong(self):
        response = self.client.get(
            f"/api/ENCODE/{self.data_repo_4dn.name}/sample_id/", 
            content_type="application/json", 
            headers=self.token_header)
        rjson = json.loads(response.data.decode())
        self.assertEqual(rjson['status'], 'error')
        self.assertEqual(rjson['http_status_code'], 400)

    def test_not_found_repository(self):
        response = self.client.get(
            f"/api/ENCODE/nonexistantrepo/sampleid/", 
            content_type="application/json",
            headers=self.token_header)
        rjson = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(rjson['http_status_code'], 404)
        
    @patch('app.download_utils.download_ENCODE_metadata')
    def test_forbidden(self, mock_download_metadata):
        mock_download_metadata.side_effect = requests.HTTPError()
        response = self.client.get(
            f"/api/ENCODE/nonexistantrepo/sampleid/", 
            content_type="application/json",
            headers=self.token_header)
        rjson = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(rjson['http_status_code'], 404)
        
    @patch('app.download_utils.download_ENCODE_metadata')
    def test_all_went_well(self, mock_download_metadata):
        mock_download_metadata.return_value = {}
        import pdb; pdb.set_trace()
        response = self.client.get(
            f"/api/ENCODE/{self.data_repo_4dn.name}/sampleid/", 
            content_type="application/json",
            headers=self.token_header)
        
        rjson = json.loads(response.data.decode())
        self.assertEqual(rjson['status'], 'ok')
        

if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
