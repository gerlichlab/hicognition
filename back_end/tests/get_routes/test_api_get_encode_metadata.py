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

class MockResponse:
    def __init__(self, content, status_code, headers={}):
        self.content = content
        self.status_code = status_code
        self.headers = headers

    def raise_for_status(self):
        if self.status_code >= 400:
            exc = requests.HTTPError(f"Mock HTTPError {self.status_code}")
            exc.response = self
            raise exc
        return

class TestGetMetadata(LoginTestCase):
    """Test get_route for encode metadata.
    Haven't tested whether correct stuff is returned, as this is already tested in
    test_download_functions"""


    def setUp(self):
        super().setUp()

        self.data_repo_4dn = DataRepository(
            name="4dn", url="thisisurl", auth_required=False, file_url="thisisurl"
        )
        db.session.add(self.data_repo_4dn)
        db.session.commit()

        self.token_header = self.get_token_header(
            self.add_and_authenticate("test", "asdf")
        )

    def test_found_repository_but_url_is_wrong(self):
        response = self.client.get(
            f"/api/ENCODE/{self.data_repo_4dn.name}/sample_id/",
            content_type="application/json",
            headers=self.token_header,
        )
        rjson = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)

    def test_not_found_repository(self):
        response = self.client.get(
            f"/api/ENCODE/nonexistantrepo/sampleid/",
            content_type="application/json",
            headers=self.token_header,
        )
        rjson = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 404)

    @patch("requests.get")
    def test_forbidden(self, mock_request):
        mock_request.return_value = MockResponse('', 403)
        
        response = self.client.get(
            f"/api/ENCODE/{self.data_repo_4dn.name}/sampleid/",
            content_type="application/json",
            headers=self.token_header,
        )
        rjson = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(rjson["http_status_code"], 403)

    @patch("requests.get")
    def test_all_went_well(self, mock_download_metadata):
        mock_download_metadata.return_value = MockResponse(
            '{"open_data_url": "thisisanurl", "file_format": {"file_format": "bed"}, "display_title":"title", "href": "thisisanurl"}',
            200,
            headers={'Application': "application/json"}
        )
        response = self.client.get(
            f"/api/ENCODE/{self.data_repo_4dn.name}/sampleid/",
            content_type="application/json",
            headers=self.token_header,
        )

        rjson = json.loads(response.data.decode())
        self.assertEqual(rjson["status"], "ok")


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
