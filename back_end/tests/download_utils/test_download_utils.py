"""Module testing the download_utils functions, like download and save file."""
from itertools import product
import json
import os
import shutil
import unittest
from unittest.mock import patch
import gzip
from requests.exceptions import HTTPError
import requests
from app.models import DataRepository, Dataset
from app import download_utils

# add path to import app
# import sys
# sys.path.append("./")


class ConcurrentTempDirTest(unittest.TestCase):
    """Creates and deletes temporary directory structures.
    First one creates tmp_dir. Last one deletes tmp_dir.
    Every instance mkdirs their own dir in tmp_dir/
    """

    TEMP_PATH = "./tmp_test"
    sub_path: str

    @classmethod
    def setUpClass(cls) -> None:
        """setup test directory if not exists"""
        if not os.path.exists(cls.TEMP_PATH):
            os.mkdir(cls.TEMP_PATH)
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        """remove test directory if empty"""
        if os.path.isdir(cls.TEMP_PATH) and len(os.listdir(cls.TEMP_PATH)) == 0:
            os.rmdir(cls.TEMP_PATH)
        return super().tearDownClass()

    @property
    def tmp_path(self):
        return os.path.join(__class__.TEMP_PATH, self.sub_path)

    def setUp(self) -> None:
        os.mkdir(self.tmp_path)
        return super().setUp()

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp_path)
        return super().tearDown()


test_cases = {
    "bedgz": {
        "file": "tests/testfiles/4DNFIRCHWS8M.bed.gz",
        "headers": {"Content-Disposition": "filename=filename.bed.gz"},
        "md5sum": "0934773585cd8b75960444d97cc3d41e",
        "filename": "filename.bed.gz",
        "filename_gunzip": "filename.bed",
        "file_gunzipped": "tests/testfiles/4DNFIRCHWS8M.bed",
    },
    "bed": {
        "file": "tests/testfiles/4DNFIRCHWS8M.bed",
        "headers": {"Content-Disposition": "filename=filename.bed"},
        "md5sum": "078fcd97876d28681a4fb593f53bfacb",
        "filename": "filename.bed",
        "filename_gunzip": "filename.bed",
    },
    "bw": {
        "file": "tests/testfiles/test.bw",
        "md5sum": "e7d9fdbf1c63245fcf93225aedfd0b49",
    },
    "bigwig": {
        "file": "tests/testfiles/test.bigwig",
        "md5sum": "e7d9fdbf1c63245fcf93225aedfd0b49",
    },
    "emptyfile": {
        "file": "tests/testfiles/empty.bed",
        "md5sum": "d41d8cd98f00b204e9800998ecf8427e",
    },
    "404": {"status_code": 404, "raises": requests.HTTPError()},
    "403": {"status_code": 403, "raises": requests.HTTPError()},
    "bedgz_json": {
        "file": "tests/testfiles/4DNFIRCHWS8M.json",
        "headers": {"Application": "application/json"},
        "type": "encode",
    },
}


def mock_http_request(*args, **kwargs):
    """requests.get mock"""

    class MockResponse:
        """Mocks an http request"""

        def __init__(self, content, status_code, headers=dict()):
            self.content = content
            self.status_code = status_code
            self.headers = headers

        def raise_for_status(self):
            if self.status_code >= 400:
                raise requests.HTTPError(f"Mock HTTPError {self.status_code}")
            return

    test_case = test_cases[args[0]]
    file_path = test_case.get("file")
    headers = test_case.get("headers", {})
    status_code = test_case.get("status_code", 200)

    content = ""
    if file_path:
        with open(file_path, "rb") as f:
            content = f.read()

    return MockResponse(content, status_code, headers)


class TestDownloadFile(ConcurrentTempDirTest):
    """Tests file download functionality"""

    sub_path = "test_download_file"

    def setUp(self) -> None:
        return super().setUp()

    @patch("requests.get", side_effect=mock_http_request)
    def test_get_correct_filename(self, mock_http_request):
        test_inputs = list(product(test_cases, [True, False]))

        for id, gunzip in test_inputs:
            test_case = test_cases[id]
            if test_case.get("status_code", 200) != 200:
                continue
            (content, name) = download_utils.download_file(id, decompress=gunzip)
            if gunzip:
                self.assertEqual(
                    name, test_case.get("filename_gunzip", test_case.get("filename"))
                )
            else:
                self.assertEqual(name, test_case.get("filename"))

    @patch("requests.get", side_effect=mock_http_request)
    def test_check_md5(self, mock_http_request):
        for id, test_case in test_cases.items():
            if test_case.get("status_code", 200) != 200:
                continue
            (content, name) = download_utils.download_file(
                id, md5sum=test_case.get("md5sum")
            )
            with self.assertRaises(download_utils.MD5Exception):
                (content, name) = download_utils.download_file(
                    id, md5sum="thisisnotvalid"
                )

    @patch("requests.get", side_effect=mock_http_request)
    def test_file_retrieval(self, mock_http_request):
        for id, test_case in test_cases.items():
            if test_case.get("status_code", 200) != 200:
                continue
            expected = ""
            if test_case.get("file"):
                with open(test_case["file"], "rb") as f:
                    expected = f.read()

            (content, name) = download_utils.download_file(id, decompress=False)
            self.assertEqual(content, expected)

    @patch("requests.get", side_effect=mock_http_request)
    def test_gunzipping(self, mock_http_request):
        for id, test_case in test_cases.items():
            if test_case.get("status_code", 200) != 200:
                continue

            expected = ""
            file_path = test_case.get("file_gunzipped", test_case.get("file"))
            with open(file_path, "rb") as f:
                expected = f.read()
            (content, name) = download_utils.download_file(id, decompress=True)
            self.assertEqual(content, expected)

    @patch("requests.get", side_effect=mock_http_request)
    def test_http_errors(self, mock_http_request):
        for id, test_case in test_cases.items():
            if test_case.get("status_code", 200) == 200:
                try:
                    download_utils.download_file(id)
                except Exception:
                    self.fail("this shouldn't raise an exception!")
            else:
                with self.assertRaises(requests.RequestException):
                    download_utils.download_file(id)

    def test_download_non_existant_urls(self):
        with self.assertRaises(requests.exceptions.MissingSchema) as context:
            download_utils.download_file("hurrthisisnoturl")
        with self.assertRaises(requests.exceptions.ConnectionError) as context:
            download_utils.download_file("http://hurrdurthisisadomain.fakedomain")
        with self.assertRaises(requests.exceptions.MissingSchema) as context:
            download_utils.download_file("a slkd .at")


class TestDownloadENCODEMetadata(ConcurrentTempDirTest):
    """Tests encode metadata downloads functionality
    This is actually hard to test, because tests should
    run offline.
    """

    def setUp(self) -> None:
        self.repository = DataRepository(
            url="{href}",
            file_url="{id}",
            name="test",
        )
        return super().setUp()

    sub_path = "test_download_encode_metadata"

    @patch("requests.get", side_effect=mock_http_request)
    def test_download_correct_sample(self, mock_http_request):
        for id, test_case in test_cases.items():
            if test_case.get("type") == "encode":
                with open(test_case["file"]) as json_file:
                    truth = json.load(json_file)
                rjson = download_utils.download_ENCODE_metadata(self.repository, id)
        self.assertEqual(rjson, truth)

    def test_download_non_existant_urls(self):  # , mock_http_request):
        with self.assertRaises(requests.exceptions.MissingSchema) as context:
            download_utils.download_ENCODE_metadata(self.repository, "hurrthisisnoturl")
        with self.assertRaises(requests.exceptions.ConnectionError) as context:
            download_utils.download_ENCODE_metadata(
                self.repository, "http://hurrdurthisisadomain.fakedomain"
            )
        with self.assertRaises(requests.exceptions.MissingSchema) as context:
            download_utils.download_ENCODE_metadata(self.repository, "a slkd .at")


class TestDownloadENCODE(ConcurrentTempDirTest):
    sub_path = "test_download_encode"

    def tearDown(self) -> None:
        return super().tearDown()

    def setUp(self):
        super().setUp()
        self.test_cases = {
            "bw": {
                "metadata": {
                    "open_data_url": "_.~*~._",
                    "display_title": "bwfile.bw",
                    "file_format": {"file_format": "bw"},
                },
                "http_content": "tests/testfiles/4DNFI29ICQ36.bw",
                "http_filename": "http_bwfile.bw",
                "correct_name": "bwfile.bw",
            },
            "bed": {
                "metadata": {
                    "open_data_url": "_.~*~._",
                    "display_title": "bedfile.bed",
                    "file_format": {"file_format": "bed"},
                },
                "http_content": "tests/testfiles/4DNFIRCHWS8M.bed",
                "http_filename": "http_bedfile.bed",
                "correct_name": "bedfile.bed",
            },
            "bedgz": {
                "metadata": {
                    "open_data_url": "_.~*~._",
                    "display_title": "bedfile.bed.gz",
                    "file_format": {"file_format": "bed"},
                },
                "http_content": "tests/testfiles/4DNFIRCHWS8M.bed.gz",
                "http_filename": "http_bedfile.bed.gz",
                "correct_name": "bedfile.bed",
            },
            "bedgz_no_filename": {
                "metadata": {
                    "open_data_url": "_.~*~._",
                    "file_format": {"file_format": "bed"},
                },
                "http_content": "tests/testfiles/4DNFIRCHWS8M.bed.gz",
                "http_filename": "http_bedfile.bed",
                "correct_name": "http_bedfile.bed",
            },
            "bedgz_no_name_at_all": {
                "metadata": {
                    "open_data_url": "_.~*~._",
                    "file_format": {"file_format": "bed"},
                },
                "http_content": "tests/testfiles/4DNFIRCHWS8M.bed.gz",
                "raises": download_utils.MetadataNotWellformed,
            },
        }
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
            name="testrepo",
            file_url="https://{id}",
            url="https://{href}",
            auth_required=False,
        )
        self.ds.repository = self.data_repo

    def test_raises_exception_timeout(self):
        with self.assertRaises(requests.exceptions.ConnectionError):
            self.data_repo.file_url = "https://thisissuchaninvalidurlithink.at/{id}"
            download_utils.download_encode(self.ds, self.tmp_path)

    @patch("app.download_utils.download_ENCODE_metadata")
    def test_raises_exception_metadatafetch(self, mock_download_ENCODE_metadata):
        mock_download_ENCODE_metadata.side_effect = HTTPError()
        with self.assertRaises(requests.exceptions.HTTPError) as context:
            download_utils.download_encode(self.ds, self.tmp_path)

    @patch("app.download_utils.download_file")
    @patch("app.download_utils.download_ENCODE_metadata")
    def test_save_files_properly(
        self, mock_download_ENCODE_metadata, mock_download_file
    ):
        for id, test_case in self.test_cases.items():
            with open(test_case["http_content"], "rb") as f:
                content = f.read()

            ret_val = (content, test_case.get("http_filename"))
            mock_download_file.return_value = ret_val
            mock_download_ENCODE_metadata.return_value = test_case.get("metadata", {})

            if not test_case.get("raises"):
                dataset = download_utils.download_encode(self.ds, self.tmp_path)

                true_temp_path = os.path.join(
                    self.tmp_path, f"1_{test_case.get('correct_name')}"
                )
                self.assertEqual(dataset.file_path, true_temp_path)
                self.assertEqual(dataset.processing_state, "uploaded")

                with open(true_temp_path, "rb") as f:
                    content_true = f.read()
                self.assertEqual(content, content_true)

                os.remove(true_temp_path)

    @patch("app.download_utils.download_ENCODE_metadata")
    @patch("app.download_utils.download_file")
    def test_raises_ioerror_when_file_exists(
        self,
        mock_download_file,
        mock_download_metadata,
    ):
        for id, test_case in self.test_cases.items():
            if test_case.get("raises"):
                continue

            # create file if not already exists
            true_temp_path = os.path.join(
                self.tmp_path, f"1_{test_case.get('correct_name')}"
            )
            if not os.path.exists(true_temp_path):
                with open(true_temp_path, "w") as f:
                    f.write("")

            # mock
            with open(test_case["http_content"], "rb") as f:
                content = f.read()
            # https://stackoverflow.com/questions/31477825/unable-to-return-a-tuple-when-mocking-a-function
            mock_download_file.return_value = content, test_case.get("http_filename")
            mock_download_metadata.return_value = test_case.get("metadata", {})

            with self.assertRaises(download_utils.FileExistsException) as context:
                download_utils.download_encode(self.ds, self.tmp_path)

            os.remove(true_temp_path)  # BAD?!


class TestDownloadURL(ConcurrentTempDirTest):
    """Tests download utils for URLs"""

    sub_path = "test_download_url"

    def setUp(self):
        super().setUp()
        # super(self.__class__, self).setUp()
        # self.TEMP_PATH = os.path.join(self.tmp_path, 'URL')
        # os.path.mkdir(self.TEMP_PATH)
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
            name="testrepo",
            file_url="https://{id}",
            url="https://{href}",
            auth_required=False,
        )
        self.ds.repository = self.data_repo

    @patch("app.download_utils.download_file")
    def test_bw_file(self, mock_download_file):
        with open("tests/testfiles/test.bw", "rb") as file:
            content = file.read()
        mock_download_file.return_value = content, "file.bw"

        download_utils.download_url(self.ds, self.tmp_path, "bw")

        true_file_path = os.path.join(self.tmp_path, "1_file.bw")

        self.assertEqual(self.ds.processing_state, "uploaded")
        self.assertEqual(self.ds.file_path, true_file_path)
        self.assertTrue(os.path.exists(self.ds.file_path))
        with open(self.ds.file_path, "rb") as file:
            to_be_tested = file.read()
        with open(true_file_path, "rb") as file:
            true_file = file.read()
        self.assertEqual(to_be_tested, true_file)

    @patch("app.download_utils.download_file")
    def test_legit_file_gunzip(self, mock_download_file):
        with open("tests/testfiles/4DNFIRCHWS8M.bed.gz", "rb") as file:
            content = gzip.decompress(file.read())
        mock_download_file.return_value = content, "file.bed"

        download_utils.download_url(self.ds, self.tmp_path, "bed")

        true_file_path = os.path.join(self.tmp_path, "1_file.bed")

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

        true_file_path = os.path.join(self.tmp_path, "1_4DNFIRCHWS8M.bed")
        with open(true_file_path, "w") as new_file:
            new_file.write("this is a file and i am here")

        with self.assertRaises(download_utils.FileExistsException):
            download_utils.download_url(self.ds, self.tmp_path, "bed")


class TestIsGzipped(unittest.TestCase):
    def test_gzipped(self):
        self.assertTrue(
            download_utils._is_gzipped(gzip.compress(str("Hello World").encode()))
        )
        self.assertFalse(download_utils._is_gzipped(str("Hello World").encode()))


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
