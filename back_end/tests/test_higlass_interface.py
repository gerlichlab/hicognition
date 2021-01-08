"""Tests for higlass_interface.py."""
import unittest
from functools import partial
import json
import os
from requests.exceptions import HTTPError
from test_helpers import TempDirTestCase
from hicognition import higlass_interface

class TestPreprocessDataset(TempDirTestCase):
    """Tests for preprocess_datasets function."""

    def test_preprocess_bed(self):
        """Test preprocessing of bedfile.

        This only tests dispatching of call and corresponding
        return code since the rest should be tested in clodius.
        """
        exit_code = higlass_interface.preprocess_dataset(
            file_type="bedfile",
            chromsizes_path="./data/hg19.chrom.sizes",
            file_path="./tests/testfiles/test3_realData_large.bed",
            output_path=os.path.join(TempDirTestCase.TEMP_PATH, "test3_realData_large.beddb"),
        )
        # test exit code
        self.assertEqual(exit_code, 0)

    def test_preprocess_bed_bad_file(self):
        """File has bad format"""
        exit_code = higlass_interface.preprocess_dataset(
            file_type="bedfile",
            chromsizes_path="./data/hg19.chrom.sizes",
            file_path="./tests/testfiles/test_bad_file_format.bed",
            output_path=os.path.join(TempDirTestCase.TEMP_PATH, "test_bad_file_format.beddb"),
        )
        # test exit code
        self.assertNotEqual(exit_code, 0)

    def test_wrong_parameters(self):
        """Test failure of clodius if the wrong parameters
        were passed."""
        # test wrong files
        exit_code = higlass_interface.preprocess_dataset(
            file_type="bedfile",
            chromsizes_path="./data/hg19.chrom.sizes",
            file_path="./tests/testfiles/test3_realData_large_false.bed",
            output_path=os.path.join(TempDirTestCase.TEMP_PATH, "test3_realData_large.beddb"),
        )
        self.assertNotEqual(exit_code, 0)

    def test_wrong_filetype(self):
        """Test raising of error when wrong filetype was passed."""
        # test wrong filetype
        badcall = partial(
            higlass_interface.preprocess_dataset,
            file_type="awesomefile",
            chromsizes_path="./data/hg19.chrom.sizes",
            file_path="./tests/testfiles/test3_realData_large_false.bed",
            output_path=os.path.join(TempDirTestCase.TEMP_PATH, "test3_realData_large.beddb"),
        )
        self.assertRaises(ValueError, badcall)

    def test_preprocess_bedpe(self):
        """Test preprocessing of bedfile.

        This only tests dispatching of call and corresponding
        return code since the rest should be tested in clodius.
        """
        exit_code = higlass_interface.preprocess_dataset(
            file_type="bedpe",
            chromsizes_path="./data/hg19.chrom.sizes",
            file_path="./tests/testfiles/test2_realData_twocol.bedpe",
            output_path=os.path.join(TempDirTestCase.TEMP_PATH, "test2_realData_twocol.bed2ddb")
        )
        # test exit code
        self.assertEqual(exit_code, 0)


class TestAddData(unittest.TestCase):
    """Test addition of data to higlass server.

    Logic of tests is to monkeypatch requests.post
    to intercept calls and see whether they are
    dispatched correctly.
    """

    def test_upload(self):
        """Test to upload a beddb file."""
        # monkeypatch requests.post
        higlass_interface.requests.post = fake_post
        fake_credentials = {"user": "asdf",
                            "password": "1234"}
        server = "test.com"
        file_path = "./tests/testfiles/test3_realData_large.beddb"
        name = "test1"
        file_type = "bedfile"
        result = higlass_interface.add_tileset(file_type, file_path, server, fake_credentials, name)
        self.assertEqual({'url': 'test.com', 'data': {'filetype': 'beddb', 'datatype': 'bedlike', 'coordSystem': 'hg19', 'name': 'test1'}},
                         result)

    def test_bad_response(self):
        """Test correct response to bad request."""
        # monkeypatch requests.post
        higlass_interface.requests.post = raising_post
        fake_credentials = {"user": "asdf",
                            "password": "1234"}
        server = "test.com"
        file_path = "./tests/testfiles/test3_realData_large.beddb"
        name = "test1"
        file_type = "bedfile"
        bad_call = partial(higlass_interface.add_tileset, file_type, file_path, server, fake_credentials, name)
        self.assertRaises(HTTPError, bad_call)


# helper classes/functions


class FakeRespone():
    """Fake response class to test add tileset"""
    def __init__(self, status_code, text):
        """Constructor of fake respone class"""
        self.status_code = status_code
        self.text = text


def fake_post(**kwargs):
    """function to replace requests.post that
    just returns the calling arguments as text"""
    # get rid of file and auth (not serializable)
    kwargs["files"]["datafile"].close()
    kwargs.pop("files")
    kwargs.pop("auth")
    return FakeRespone(201, json.dumps(kwargs))


def raising_post(**kwargs):
    """function to replace requests.post that
    returns a failed request"""
    # Close file again
    kwargs["files"]["datafile"].close()
    return FakeRespone(400, "")


if __name__ == "__main__":
    RESULT = unittest.main(verbosity=3, exit=False)
