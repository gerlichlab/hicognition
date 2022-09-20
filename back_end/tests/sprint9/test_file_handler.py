"""Module testing the file handler functions, like download and save file."""
import unittest
from unittest.mock import patch
from requests.exceptions import HTTPError
import requests
import pandas as pd
import numpy as np
from hicognition.test_helpers import TempDirTestCase

from app.file_handler import download_file, save_file

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
        
        


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)