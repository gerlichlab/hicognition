"""Module testing the file handler functions, like download and save file."""
import json
import unittest
from unittest.mock import patch
from requests.exceptions import HTTPError
import requests
from app.models import DataRepository
from hicognition.test_helpers import TempDirTestCase
from app import db

from app.download_functions import download_ENCODE_metadata, download_file

# add path to import app
# import sys
# sys.path.append("./")

class TestDownloadFile(TempDirTestCase):
    """Tests file handler functionality"""

    def setUp(self):
        # TODO setUp runs twice?!

        super(TestDownloadFile, self).setUp()
        
    # TODO learn when to use patch @ decorator
    # TODO test_helpers.py should remove tmp_test if exists

    def mock_http_request(*args, **kwargs):
        class MockResponse:
            def __init__(self, content, status_code, headers = {}):
                self.content = content
                self.status_code = status_code
                self.headers = headers

            def raise_for_status(self):
                if self.status_code >= 400:
                    raise requests.HTTPError(f'Mock HTTPError {self.status_code}')
                return

        if args[0] == 'https://mockurl.mock/200':
            with open('tests/testfiles/4DNFIRCHWS8M.bed.gz', 'rb') as file:
                return MockResponse(file.read(), 200, headers={'Content-Disposition':'filename=filename.json'})
        if args[0] == 'https://mockurl.mock/200_no_filename':
            with open('tests/testfiles/4DNFIRCHWS8M.bed.gz', 'rb') as file:
                return MockResponse(file.read(), 200, headers={})
        if args[0] == 'https://mockurl.mock/200_but_no_file':
            with open('tests/testfiles/4DNFIRCHWS8M.bed.gz', 'rb') as file:
                return MockResponse('', 200, headers={})
        if args[0] == 'https://mockurl.mock/404':
            return MockResponse('', 404)
        return MockResponse('', 404)


    @patch('requests.get', side_effect=mock_http_request)
    def test_download_existing_file(self, mock_http_request):
        name, content = download_file("https://mockurl.mock/200")
        self.assertEqual(name, 'filename.json')
        with open('tests/testfiles/4DNFIRCHWS8M.bed.gz', 'rb') as bedgzfile:
            self.assertEqual(content, bedgzfile.read())
    
    @patch('requests.get', side_effect=mock_http_request)
    def test_download_existing_file_wo_name(self, mock_http_request):
        name, content = download_file("https://mockurl.mock/200_no_filename")
        self.assertIsNone(name)
        with open('tests/testfiles/4DNFIRCHWS8M.bed.gz', 'rb') as bedgzfile:
            self.assertEqual(content, bedgzfile.read())

    @patch('requests.get', side_effect=mock_http_request)
    def test_download_file_empty(self, mock_http_request):
        with self.assertRaises(HTTPError) as context:
            download_file("https://mockurl.mock/200_but_no_file")
        self.assertTrue('File was empty' in str(context.exception))
    
    @patch('requests.get', side_effect=mock_http_request)
    def test_download_40x(self, mock_http_request):
        with self.assertRaises(HTTPError) as context:
            download_file("https://mockurl.mock/404")
        self.assertTrue('404' in str(context.exception))
        
        
class TestDownloadENCODEMetadata(TempDirTestCase):
    """Tests encode metadata downloads functionality
    This is actually hard to test, because tests should
    rund offline.
    """

    def setUp(self):
        super(self.__class__, self).setUp()
        # self.repo1 = DataRepository( # do we even need that? if no repo specified use none
        #     name = "4dn",
        #     url = "https://data.4dnucleome.org/files-processed/{id}", # TODO bed gz evil
        #     auth_required = False
        # )
        # db.session.add(self.repo1)
        # db.session.commit()
        
    # TODO learn when to use patch @ decorator
    # TODO test_helpers.py should remove tmp_test if exists

    def mock_http_request(*args, **kwargs):
        class MockResponse:
            def __init__(self, content, status_code, headers = {}):
                self.content = content
                self.status_code = status_code
                self.headers = headers

            def raise_for_status(self):
                if self.status_code >= 400:
                    raise requests.HTTPError(f'Mock HTTPError {self.status_code}')
                return

        if args[0] == 'https://mockurl.mock/200':
            with open('tests/testfiles/4DNFIRCHWS8M.json', 'r') as file:
                return MockResponse(file.read(), 200, headers={'Application': 'application/json'})
        if args[0] == 'https://mockurl.mock/404':
            return MockResponse('', 404, headers={})
        if args[0] == 'https://mockurl.mock/403':
                return MockResponse('', 403, headers={})
        return MockResponse('', 404)


    @patch('requests.get', side_effect=mock_http_request)
    def test_download_correct_sample(self, mock_http_request):
        response_json = download_ENCODE_metadata("https://mockurl.mock/200")
        self.assertEqual(response_json['status'], 'ok')
        self.assertEqual(response_json['http_status_code'], 200)
        with open('tests/testfiles/4DNFIRCHWS8M.json') as json_file:
            truth = json.load(json_file)
        self.assertEqual(response_json['json'], truth)
    
    @patch('requests.get', side_effect=mock_http_request)
    def test_download_sample_id_wrong(self, mock_http_request):
        response_json = download_ENCODE_metadata("https://mockurl.mock/404")
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['http_status_code'], 404)
        

    @patch('requests.get', side_effect=mock_http_request)
    def test_download_forbidden(self, mock_http_request):
        response_json = download_ENCODE_metadata("https://mockurl.mock/403")
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['http_status_code'], 403)
    
   # @patch('requests.get', side_effect=mock_http_request)
    def test_download_non_existant_urls(self):#, mock_http_request):
        with self.assertRaises(requests.exceptions.MissingSchema) as context:
            download_file("hurrthisisnoturl")
        with self.assertRaises(requests.exceptions.ConnectionError) as context:
            download_file("http://so.ill.add.subdomains.hurrthisisnoturlbutitcouldbe.at")
        with self.assertRaises(requests.exceptions.MissingSchema) as context:
            download_file("a slkd .at")
        
        



if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)