"""Helper functions and classes for unittesting"""
import unittest
import os
import shutil


class TempDirTestCase(unittest.TestCase):
    """Will create a temporary directory in the current working 
    directory once before all tests are run that is available via 
    self.tempdir. Removes the directory and all content after
    all tests have been run."""

    @classmethod
    def setUpClass(cls):
        """make test directory."""
        os.mkdir("./tmp_test")
        cls.tempdir = "./tmp_test"

    @classmethod
    def tearDownClass(cls):
        """remove test directory"""
        shutil.rmtree("./tmp_test")
