"""Module testing the file handler functions, like download and save file."""
import json
import os
import unittest
from unittest.mock import patch
from requests.exceptions import HTTPError
import requests
import gzip
from app.models import DataRepository, Dataset
from hicognition.test_helpers import TempDirTestCase

import app.download_utils as download_utils

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
            def __init__(self, content, status_code, headers={}):
                self.content = content
                self.status_code = status_code
                self.headers = headers

            def raise_for_status(self):
                if self.status_code >= 400:
                    raise requests.HTTPError(f"Mock HTTPError {self.status_code}")
                return

        if args[0] == "https://mockurl.mock/200":
            with open("tests/testfiles/4DNFIRCHWS8M.bed.gz", "rb") as file:
                return MockResponse(
                    file.read(),
                    200,
                    headers={"Content-Disposition": "filename=filename.bed.gz"},
                )
        if args[0] == "https://mockurl.mock/200_no_filename":
            with open("tests/testfiles/4DNFIRCHWS8M.bed.gz", "rb") as file:
                return MockResponse(file.read(), 200, headers={})
        if args[0] == "https://mockurl.mock/200_but_no_file":
            with open("tests/testfiles/4DNFIRCHWS8M.bed.gz", "rb") as file:
                return MockResponse("", 200, headers={})
        if args[0] == "https://mockurl.mock/404":
            return MockResponse("", 404)
        return MockResponse("", 404)

    @patch("requests.get", side_effect=mock_http_request)
    def test_download_existing_file(self, mock_http_request):
        content, name = download_utils.download_file(
            "https://mockurl.mock/200",
            md5sum="0934773585cd8b75960444d97cc3d41e",
            gunzip_if_compressed=False,
        )
        self.assertEqual(name, "filename.bed.gz")
        with open("tests/testfiles/4DNFIRCHWS8M.bed.gz", "rb") as bedgzfile:
            self.assertEqual(content, bedgzfile.read())
        with self.assertRaises(download_utils.MD5Error):
            content, name = download_utils.download_file(
                "https://mockurl.mock/200", md5sum="00000000000000000000000000000000"
            )

    @patch("requests.get", side_effect=mock_http_request)
    def test_download_existing_file_wo_name(self, mock_http_request):
        content, name = download_utils.download_file(
            "https://mockurl.mock/200_no_filename", gunzip_if_compressed=False
        )
        self.assertIsNone(name)
        with open("tests/testfiles/4DNFIRCHWS8M.bed.gz", "rb") as bedgzfile:
            self.assertEqual(content, bedgzfile.read())

    @patch("requests.get", side_effect=mock_http_request)
    def test_download_file_empty(self, mock_http_request):
        with self.assertRaises(download_utils.FileEmptyError) as context:
            download_utils.download_file("https://mockurl.mock/200_but_no_file")
        self.assertTrue("File was empty" in str(context.exception))

    @patch("requests.get", side_effect=mock_http_request)
    def test_download_40x(self, mock_http_request):
        with self.assertRaises(HTTPError) as context:
            download_utils.download_file("https://mockurl.mock/404")
        self.assertTrue("404" in str(context.exception))


class TestDownloadENCODEMetadata(TempDirTestCase):
    """Tests encode metadata downloads functionality
    This is actually hard to test, because tests should
    rund offline.
    """

    def setUp(self):
        super(self.__class__, self).setUp()

    def mock_http_request(*args, **kwargs):
        class MockResponse:
            def __init__(self, content, status_code, headers={}):
                self.content = content
                self.status_code = status_code
                self.headers = headers

            def raise_for_status(self):
                if self.status_code >= 400:
                    raise requests.HTTPError(f"Mock HTTPError {self.status_code}")
                return

        if args[0] == "https://mockurl.mock/200":
            with open("tests/testfiles/4DNFIRCHWS8M.json") as file:
                return MockResponse(
                    file.read(), 200, headers={"Application": "application/json"}
                )
        if args[0] == "https://mockurl.mock/404":
            return MockResponse("", 404, headers={"Application": "application/json"})
        if args[0] == "https://mockurl.mock/403":
            with open("tests/testfiles/4DNFIRCHWS8M.json") as file:
                return MockResponse(
                    "", 403, headers={"Application": "application/json"}
                )

        return None

    @patch("requests.get", side_effect=mock_http_request)
    def test_download_correct_sample(self, mock_http_request):
        response_json = download_utils.download_ENCODE_metadata(
            "https://mockurl.mock/200"
        )
        with open("tests/testfiles/4DNFIRCHWS8M.json") as json_file:
            truth = json.load(json_file)
        self.assertEqual(response_json, truth)

    @patch("requests.get", side_effect=mock_http_request)
    def test_download_sample_id_wrong(self, mock_http_request):
        with self.assertRaises(requests.exceptions.HTTPError) as context:
            download_utils.download_ENCODE_metadata("https://mockurl.mock/404")

    @patch("requests.get", side_effect=mock_http_request)
    def test_download_forbidden(self, mock_http_request):
        with self.assertRaises(requests.exceptions.HTTPError) as context:
            download_utils.download_ENCODE_metadata("https://mockurl.mock/403")

    # @patch('requests.get', side_effect=mock_http_request)
    def test_download_non_existant_urls(self):  # , mock_http_request):
        with self.assertRaises(requests.exceptions.MissingSchema) as context:
            download_utils.download_file("hurrthisisnoturl")
        with self.assertRaises(requests.exceptions.ConnectionError) as context:
            download_utils.download_file(
                "http://so.ill.add.subdomains.hurrdurthisisaninvaliddomain.fakedomain"
            )
        with self.assertRaises(requests.exceptions.MissingSchema) as context:
            download_utils.download_file("a slkd .at")


class TestDownloadENCODE(TempDirTestCase):  # DEFINE how i want to get info from this.
    def setUp(self):
        super(self.__class__, self).setUp()
        self.ds = Dataset(
            id=1,
            dataset_name="name",
            filetype="bedfile",
            processing_state="uploading",
            user_id=1,
            assembly=1,
            sizeType="Point",
            source_url="valid_url.at/bed.bed.gz",
            repository_name="testrepo",
            sample_id="test_sample",
        )
        self.data_repo = DataRepository(
            name="testrepo", url="https://{id}", auth_required=False
        )
        self.ds.repository = self.data_repo

    @patch("app.download_utils.download_ENCODE_metadata")
    def test_raises_exception_metadatafetch(self, mock_download_ENCODE_metadata):
        mock_download_ENCODE_metadata.side_effect = HTTPError()
        with self.assertRaises(download_utils.MetadataFetchError) as context:
            download_utils.download_encode(self.ds, TempDirTestCase.TEMP_PATH)

    @patch("app.download_utils.download_ENCODE_metadata")
    def test_raises_exception_metadataerror(self, mock_download_ENCODE_metadata):
        mock_download_ENCODE_metadata.return_value = {}
        with self.assertRaises(download_utils.MetadataError) as context:
            download_utils.download_encode(self.ds, TempDirTestCase.TEMP_PATH)

    @patch("app.download_utils.download_ENCODE_metadata")
    @patch("app.download_utils.download_file")
    def test_raises_ioerror_when_file_exists(
        self, mock_download_file, mock_download_ENCODE_metadata
    ):
        with open("tests/testfiles/4DNFIRCHWS8M.json") as json_file:
            mock_download_ENCODE_metadata.return_value = json.load(json_file)
        true_file_path = os.path.join(TempDirTestCase.TEMP_PATH, "1_4DNFIRCHWS8M.bed")
        with open(true_file_path, "w") as new_file:
            new_file.write("this is a file and i am here")

        with open("tests/testfiles/4DNFIRCHWS8M.bed.gz", "rb") as file:
            content = file.read()
            mock_download_file.return_value = content, "4DNFIRCHWS8M.bed"

        with self.assertRaises(IOError) as context:
            download_utils.download_encode(self.ds, TempDirTestCase.TEMP_PATH)

    @patch("app.download_utils.download_ENCODE_metadata")
    @patch("app.download_utils.download_file")
    def test_valid_sample_id(self, mock_download_file, mock_download_ENCODE_metadata):
        with open("tests/testfiles/4DNFIRCHWS8M.json") as json_file:
            mock_download_ENCODE_metadata.return_value = json.load(json_file)
            mock_download_ENCODE_metadata.return_value[
                "display_title"
            ] = "filename.bed.gz"
        with open("tests/testfiles/4DNFIRCHWS8M.bed.gz", "rb") as file:
            content = gzip.decompress(file.read())
            mock_download_file.return_value = content, "filename.bed"

        true_file_path = os.path.join(TempDirTestCase.TEMP_PATH, "1_filename.bed")
        ds = download_utils.download_encode(self.ds, TempDirTestCase.TEMP_PATH)
        self.assertEqual(ds.processing_state, "uploaded")
        self.assertTrue(os.path.exists(true_file_path))
        with open(true_file_path, "r") as file:
            new_content = file.read()
        self.assertEqual(content.decode(), new_content)

    @patch("app.download_utils.download_file")
    def test_file_exists(self, mock_download_file):
        with open("tests/testfiles/4DNFIRCHWS8M.bed.gz", "rb") as file:
            content = file.read()
        mock_download_file.return_value = content, "4DNFIRCHWS8M.bed.gz"

        true_file_path = os.path.join(TempDirTestCase.TEMP_PATH, "1_4DNFIRCHWS8M.bed")
        with open(true_file_path, "w") as new_file:
            new_file.write("this is a file and i am here")

        with self.assertRaises(IOError):
            download_utils.download_url(self.ds, TempDirTestCase.TEMP_PATH, "bed")


class TestDownloadURL(TempDirTestCase):  # DEFINE how i want to get info from this.
    def setUp(self):
        super(self.__class__, self).setUp()
        self.ds = Dataset(
            id=1,
            dataset_name="name",
            filetype="bedfile",
            processing_state="uploading",
            user_id=1,
            assembly=1,
            sizeType="Point",
            source_url="valid_url.at/bed.bed.gz",
            repository_name="testrepo",
            sample_id="test_sample",
        )
        self.data_repo = DataRepository(
            name="testrepo", url="https://{id}", auth_required=False
        )
        self.ds.repository = self.data_repo

    @patch("app.download_utils.download_file")
    def test_legit_file_gunzip(self, mock_download_file):
        with open("tests/testfiles/4DNFIRCHWS8M.bed.gz", "rb") as file:
            content = gzip.decompress(file.read())
        mock_download_file.return_value = content, "file.bed"

        download_utils.download_url(self.ds, TempDirTestCase.TEMP_PATH, "bed")

        true_file_path = os.path.join(TempDirTestCase.TEMP_PATH, "1_file.bed")

        self.assertEqual(self.ds.processing_state, "uploaded")
        self.assertEqual(self.ds.file_path, true_file_path)
        self.assertTrue(os.path.exists(self.ds.file_path))
        with open(self.ds.file_path) as file:
            to_be_tested = file.read()
        with open(true_file_path) as file:
            true_file = file.read()
        self.assertEqual(to_be_tested, true_file)

    @patch("app.download_utils.download_file")
    def test_file_exists(self, mock_download_file):
        with open("tests/testfiles/4DNFIRCHWS8M.bed.gz", "rb") as file:
            content = file.read()
        mock_download_file.return_value = content, "4DNFIRCHWS8M.bed.gz"

        true_file_path = os.path.join(TempDirTestCase.TEMP_PATH, "1_4DNFIRCHWS8M.bed")
        with open(true_file_path, "w") as new_file:
            new_file.write("this is a file and i am here")

        with self.assertRaises(IOError):
            download_utils.download_url(self.ds, TempDirTestCase.TEMP_PATH, "bed")


class TestIsGzipped(unittest.TestCase):
    def test_gzipped(self):
        self.assertTrue(
            download_utils._is_gzipped(gzip.compress(str("Hello World").encode()))
        )
        self.assertFalse(download_utils._is_gzipped(str("Hello World").encode()))


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
