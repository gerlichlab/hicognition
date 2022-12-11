"""Module with tests realted adding datasets."""
import os
import io
import json
import unittest
from unittest.mock import patch
from hicognition.test_helpers import LoginTestCase, TempDirTestCase
from pydantic import ValidationError

# add path to import app
# import sys
# sys.path.append("./")
from app.models import Dataset, Assembly
from app.form_models import FileDatasetPostModel, URLDatasetPostModel
from app import db

# TODO do tests for encode + url
class TestFileDatasetPostModel(LoginTestCase):
    """Tests the pydantic FileDatasetPostModel which validates the form for posting datasets."""

    maxDiff = None

    def setUp(self):
        super().setUp()
        # add assembly
        self.hg19 = Assembly(
            id=1,
            name="hg19",
            chrom_sizes=self.app.config["CHROM_SIZES"],
            chrom_arms=self.app.config["CHROM_ARMS"],
        )
        db.session.add(self.hg19)
        db.session.commit()
        # add token headers
        token = self.add_and_authenticate("test", "asdf")
        # create token_header
        self.token_headers = self.get_token_header(token)
        # add content-type
        self.token_headers["Content-Type"] = "multipart/form-data"

    def test_pydantic_model_unsupported_filetype(self):
        """Test of wrong 'cooling' filetype."""
        test_object = {
            "datasetName": "test",
            "description": "test-description",
            "assembly": "1",
            "cellCycleStage": "asynchronous",
            "perturbation": "No perturbation",
            "public": "false",
            "ValueType": "Interaction",
            "Method": "HiC",
            "Normalization": "ICCF",
            "filetype": "cooling",
            "filename": "test.mcool",
        }
        with self.assertRaises(ValidationError) as exc:
            data_ojb = FileDatasetPostModel(**test_object)
        print(exc.exception)
        assert "Unsupported filetype!" in str(exc.exception)

    def test_pydantic_model_working_cooler(self):
        """Test of correct cooler POST form."""
        test_object = {
            "datasetName": "test",
            "description": "test-description",
            "assembly": "1",
            "cellCycleStage": "asynchronous",
            "perturbation": "No perturbation",
            "public": "false",
            "ValueType": "Interaction",
            "Method": "HiC",
            "Normalization": "ICCF",
            "filetype": "cooler",
            "filename": "test.mcool",
        }
        expected_object = {
            "dataset_name": "test",
            "description": "test-description",
            "assembly": 1,
            "cell_cycle_stage": "asynchronous",
            "perturbation": "No perturbation",
            "public": False,
            "value_type": "Interaction",
            "method": "HiC",
            "normalization": "ICCF",
            "filetype": "cooler",
            "filename": "test.mcool",
            "processing_state": None,
            "protein": "undefined",
            "directionality": "undefined",
            "derivation_type": "undefined",
            "size_type": "undefined",
        }
        data_ojb = FileDatasetPostModel(**test_object)
        self.assertEqual(expected_object, data_ojb.dict())

    def test_pydantic_model_working_bed(self):
        """Test of correct bed POST form."""
        test_object = {
            "datasetName": "test",
            "description": "test-description",
            "assembly": "1",
            "cellCycleStage": "asynchronous",
            "perturbation": "No perturbation",
            "public": "false",
            "ValueType": "GenomeAnnotation",
            "SizeType": "Point",
            "filetype": "bedfile",
            "filename": "test.bed",
            "Directionality": "+",
        }
        expected_object = {
            "dataset_name": "test",
            "description": "test-description",
            "assembly": 1,
            "cell_cycle_stage": "asynchronous",
            "perturbation": "No perturbation",
            "public": False,
            "value_type": "GenomeAnnotation",
            "method": "undefined",
            "normalization": "undefined",
            "filetype": "bedfile",
            "filename": "test.bed",
            "processing_state": None,
            "protein": "undefined",
            "directionality": "+",
            "derivation_type": "undefined",
            "size_type": "Point",
        }
        data_ojb = FileDatasetPostModel(**test_object)
        self.assertEqual(expected_object, data_ojb.dict())

    def test_pydantic_model_working_cooler_wo_description(self):
        """Test of correct cooler POST form."""
        test_object = {
            "datasetName": "test",
            "description": "null",
            "assembly": "1",
            "cellCycleStage": "asynchronous",
            "perturbation": "No perturbation",
            "public": "false",
            "ValueType": "Interaction",
            "Method": "HiC",
            "Normalization": "ICCF",
            "filetype": "cooler",
            "filename": "test.mcool",
        }
        expected_object = {
            "dataset_name": "test",
            "description": "No description provided",
            "assembly": 1,
            "cell_cycle_stage": "asynchronous",
            "perturbation": "No perturbation",
            "public": False,
            "value_type": "Interaction",
            "method": "HiC",
            "normalization": "ICCF",
            "filetype": "cooler",
            "filename": "test.mcool",
            "processing_state": None,
            "protein": "undefined",
            "directionality": "undefined",
            "derivation_type": "undefined",
            "size_type": "undefined",
        }
        data_ojb = FileDatasetPostModel(**test_object)
        self.assertEqual(expected_object, data_ojb.dict())

    def test_pydantic_model_unsupported_field(self):
        """Test of if additional field was added to form."""
        test_object = {
            "datasetName": "test",
            "description": "test-description",
            "assembly": "1",
            "malicious": "True",
            "cellCycleStage": "asynchronous",
            "perturbation": "No perturbation",
            "public": "false",
            "ValueType": "Interaction",
            "Method": "HiC",
            "Normalization": "ICCF",
            "filetype": "cooler",
            "filename": "test.mcool",
        }
        with self.assertRaises(ValidationError) as exc:
            data_ojb = FileDatasetPostModel(**test_object)
        print(exc.exception)
        assert "extra fields not permitted" in str(exc.exception)

    def test_pydantic_model_wrong_fileending(self):
        """Test wrong fileending for cooler."""
        test_object = {
            "datasetName": "test",
            "description": "test-description",
            "assembly": "1",
            "cellCycleStage": "asynchronous",
            "perturbation": "No perturbation",
            "public": "false",
            "ValueType": "Interaction",
            "Method": "HiC",
            "Normalization": "ICCF",
            "filetype": "cooler",
            "filename": "test.bed",
        }
        with self.assertRaises(ValidationError) as exc:
            data_ojb = FileDatasetPostModel(**test_object)
        print(exc.exception)
        assert "Invalid filename!" in str(exc.exception)

    def test_pydantic_model_wrong_value_type(self):
        """Test wrong value_type for cooler."""
        test_object = {
            "datasetName": "test",
            "description": "test-description",
            "assembly": "1",
            "cellCycleStage": "asynchronous",
            "perturbation": "No perturbation",
            "public": "false",
            "ValueType": "Peak",
            "Method": "HiC",
            "Normalization": "ICCF",
            "filetype": "cooler",
            "filename": "test.mcool",
        }
        with self.assertRaises(ValidationError) as exc:
            data_ojb = FileDatasetPostModel(**test_object)
        print(exc.exception)
        assert "Unsupported value_type!" in str(exc.exception)

    def test_pydantic_method_not_defined(self):
        """Only GenomeAnnotation should allow an undefined method."""
        test_object = {
            "datasetName": "test",
            "description": "test-description",
            "assembly": "1",
            "cellCycleStage": "asynchronous",
            "perturbation": "No perturbation",
            "public": "false",
            "ValueType": "Interaction",
            "Normalization": "ICCF",
            "filetype": "cooler",
            "filename": "test.mcool",
        }
        with self.assertRaises(ValidationError) as exc:
            data_ojb = FileDatasetPostModel(**test_object)
        print(exc.exception)
        assert "Unsupported possible value" in str(exc.exception)

    def test_pydantic_model_wrong_value_for_meta_data(self):
        """Test wrong fileending for cooler."""
        test_object = {
            "datasetName": "test",
            "description": "test-description",
            "assembly": "1",
            "cellCycleStage": "asynchronous",
            "perturbation": "No perturbation",
            "public": "false",
            "ValueType": "Interaction",
            "Method": "microC",  # This should not be possible
            "Normalization": "ICCF",
            "filetype": "cooler",
            "filename": "test.mcool",
        }
        with self.assertRaises(ValidationError) as exc:
            data_ojb = FileDatasetPostModel(**test_object)
        print(exc.exception)
        assert "Unsupported possible value" in str(exc.exception)

    def test_reverse_alias(self):
        """Test if the reverse alias is working."""
        test_object = {
            "datasetName": "test",
            "description": "null",
            "assembly": "1",
            "cellCycleStage": "asynchronous",
            "perturbation": "No perturbation",
            "public": "false",
            "ValueType": "Interaction",
            "Method": "HiC",
            "Normalization": "ICCF",
            "filetype": "cooler",
            "filename": "test.mcool",
        }
        data_ojb = FileDatasetPostModel(**test_object)
        assert data_ojb["Normalization"] == data_ojb["normalization"]
        assert data_ojb["Normalization"] == "ICCF"


# class TestURLDatasetPostModel(LoginTestCase, TempDirTestCase):
#     """Tests the pydantic FileDatasetPostModel which validates the form for posting datasets."""

#     maxDiff = None

#     def setUp(self):
#         super().setUp()
#         # add assembly
#         self.hg19 = Assembly(
#             id=1,
#             name="hg19",
#             chrom_sizes=self.app.config["CHROM_SIZES"],
#             chrom_arms=self.app.config["CHROM_ARMS"],
#         )
#         db.session.add(self.hg19)
#         db.session.commit()
#         # add token headers
#         token = self.add_and_authenticate("test", "asdf")
#         # create token_header
#         self.token_headers = self.get_token_header(token)
#         # add content-type
#         self.token_headers["Content-Type"] = "multipart/form-data"


#         self.valid_data = {
#             "datasetName": "test",
#             "description": "test-description",
#             "assembly": "1",
#             "cellCycleStage": "asynchronous",
#             "perturbation": "No perturbation",
#             "public": "false",
#             "ValueType": "GenomeAnnotation",
#             "SizeType": "Point",
#             "filetype": "bedfile",
#             "Directionality": "+",
#             "sourceURL": "http://thisisbed.bed"
#         }

#         validation_error_testcases = {
#             'sourceURL_missing': {
#                 "sourceURL": None,
#                 "sourcseURL": "http://thisisbed.bed"
#             },
#             'name_missing': {
#                 "datasetName": None
#             },
#             '': {
#                 "sourceURL": None,
#                 "sourcseURL": "http://thisisbed.bed"
#             },
#             'sourceURL_missing': {
#                 "sourceURL": None,
#                 "sourcseURL": "http://thisisbed.bed"
#             },
#         }

#     def test_invalid_data(self):
#         for k in self.valid_data.keys():
#             temp_data = self.valid_data.copy()
#             temp_data[k] = None
#             with self.assertRaises(ValueError):
#                 URLDatasetPostModel(**temp_data)


#     def test_working_bed(self):
#         """Test of correct bed POST form."""
#         test_object = {
#             "datasetName": "test",
#             "description": "test-description",
#             "assembly": "1",
#             "cellCycleStage": "asynchronous",
#             "perturbation": "No perturbation",
#             "public": "false",
#             "ValueType": "GenomeAnnotation",
#             "SizeType": "Point",
#             "filetype": "bedfile",
#             "Directionality": "+",
#             "sourcseURL": "http://thisisbed.bed"
#         }
#         expected_object = {
#             "dataset_name": "test",
#             "description": "test-description",
#             "assembly": 1,
#             "cell_cycle_stage": "asynchronous",
#             "perturbation": "No perturbation",
#             "public": False,
#             "value_type": "GenomeAnnotation",
#             "method": "undefined",
#             "normalization": "undefined",
#             "filetype": "bedfile",
#             "processing_state": None,
#             "protein": "undefined",
#             "directionality": "+",
#             "derivation_type": "undefined",
#             "size_type": "Point",
#             "user_id": None,
#             "source_url": "http://thisisbed.bed"
#         }
#         data_ojb = URLDatasetPostModel(**test_object)
#         self.assertEqual(expected_object, data_ojb.dict())

if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
