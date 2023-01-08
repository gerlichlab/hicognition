"""Module with tests realted adding datasets."""
import os
import io
import json
from itertools import chain, combinations, product
import unittest
from unittest.mock import patch
from tests.test_utils.test_helpers import LoginTestCase, TempDirTestCase
from pydantic import ValidationError

# add path to import app
# import sys
# sys.path.append("./")
from app.models import Dataset, Assembly
from app.form_models import FileDatasetPostModel, URLDatasetPostModel, DatasetPutModel
from app import db

def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

valid_names = {
    "dataset_name": ["datasetName", "dataset_name"],
    "public": ["Public", "public"],
    "description": ["Description", "description"],
    "perturbation": ["Perturbation", "perturbation"],
    "cellCycleStage": ["Cell cycle Stage", "cellCycleStage"],
    "method": ["Method", "method"],
    "normalization": ["Normalization", "normalization"],
    "derivationType": ["DerivationType", "derivationType"],
    "protein": ["Protein", "protein"],
    "directionality": ["Directionality", "directionality"],
    "valueType": ["ValueType", "valueType"],
    "metadata_json": ["metadata_json"],
}

valid_data = {
    "dataset_name": ["thi", "dataset name this is"],
    "public": [True, False],
    "description": ["this is a description", "", "."],
    "perturbation": ["this is something"],
    "cellCycleStage": ["this is some string"],
    "method": ["this is some string"],
    "normalization": ["this is some string"],
    "derivationType": ["this is some string"],
    "protein": ["this is some string"],
    "directionality": ["this is some string"],
    "valueType": ["this is some string"],
    "metadata_json": ["{}", '{"protein": "this is some protein"}'],
}
    

class TestDatasetPutModel(LoginTestCase):
    """Will test pydantic form model of put/modify route for datasets"""
    
    def setUp(self):
        super().setUp()
        
        self.keys_powerset = list(powerset(valid_names.keys()))
        self.valid_inputs = [list(product(*[valid_names[k] for k in keys])) for keys in self.keys_powerset]
        self.valid_input_names = [args for sublist in self.keys_powerset for args in sublist]

    def test_valid_entries(self):
        # valid_keys = powerset(valid_names.keys())
        # for keys in valid_keys:
        #     if len(keys) > 5:
        #         break
        #     valid_inputs = product(*[valid_names[k] for k in keys])
        #     valid_values = product(*[valid_data[k] for k in keys])
        #     for args in product(valid_inputs, valid_values):
        #         with self.subTest(input_args = args):
        #             DatasetPutModel(**{args[0][i]: args[1][i] for i in range(0,len(args[0]))})
        #             # should not throw exceptions
        with self.subTest('valid1'):
            DatasetPutModel(**{valid_names[k][0]: valid_data[k][0] for k in valid_names.keys()})

# TODO do tests for encode + url
class TestFileDatasetPostModel(LoginTestCase):
    """Tests the pydantic FileDatasetPostModel which validates the form for posting datasets."""

    maxDiff = None

    def setUp(self):
        super().setUp()

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
            "sizeType": ''
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
            "sizeType": ''
        }
        expected_object = {
            "dataset_name": "test",
            "description": "test-description",
            "assembly": 1,
            "cellCycleStage": "asynchronous",
            "perturbation": "No perturbation",
            "public": False,
            "valueType": "Interaction",
            "method": "HiC",
            "normalization": "ICCF",
            "filetype": "cooler",
            "filename": "test.mcool",
            "protein": "undefined",
            "directionality": "undefined",
            "derivationType": "undefined",
            "sizeType": None,
            "metadata_json": {}
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
            "cellCycleStage": "asynchronous",
            "perturbation": "No perturbation",
            "public": False,
            "valueType": "GenomeAnnotation",
            "method": "undefined",
            "normalization": "undefined",
            "filetype": "bedfile",
            "filename": "test.bed",
            "protein": "undefined",
            "directionality": "+",
            "derivationType": "undefined",
            "sizeType": "Point",
            "metadata_json": {}
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
            "sizeType": ''
        }
        expected_object = {
            "dataset_name": "test",
            "description": "No description provided",
            "assembly": 1,
            "cellCycleStage": "asynchronous",
            "perturbation": "No perturbation",
            "public": False,
            "valueType": "Interaction",
            "method": "HiC",
            "normalization": "ICCF",
            "filetype": "cooler",
            "filename": "test.mcool",
            "protein": "undefined",
            "directionality": "undefined",
            "derivationType": "undefined",
            "sizeType": None,
            "metadata_json": {}
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
            "sizeType": ''
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
            "sizeType": ''
        }
        with self.assertRaises(ValidationError) as exc:
            data_ojb = FileDatasetPostModel(**test_object)

# TODO: this functionality was apparently removed from pydantic. check whether still needed
    # def test_pydantic_model_wrong_valueType(self):
    #     """Test wrong valueType for cooler."""
    #     test_object = {
    #         "datasetName": "test",
    #         "description": "test-description",
    #         "assembly": "1",
    #         "cellCycleStage": "asynchronous",
    #         "perturbation": "No perturbation",
    #         "public": "false",
    #         "ValueType": "Peak",
    #         "Method": "HiC",
    #         "Normalization": "ICCF",
    #         "filetype": "cooler",
    #         "filename": "test.mcool",
    #         "sizeType": ''
    #     }
    #     with self.assertRaises(ValidationError) as exc:
    #         data_ojb = FileDatasetPostModel(**test_object)
    #     print(exc.exception)
    #     assert "Unsupported valueType!" in str(exc.exception)
# TODO: this functionality was apparently removed from pydantic. check whether still needed
    # def test_pydantic_method_not_defined(self):
    #     """Only GenomeAnnotation should allow an undefined method."""
    #     test_object = {
    #         "datasetName": "test",
    #         "description": "test-description",
    #         "assembly": "1",
    #         "cellCycleStage": "asynchronous",
    #         "perturbation": "No perturbation",
    #         "public": "false",
    #         "ValueType": "Interaction",
    #         "Normalization": "ICCF",
    #         "filetype": "cooler",
    #         "filename": "test.mcool",
    #         "sizeType": ''
    #     }
    #     with self.assertRaises(ValidationError) as exc:
    #         data_ojb = FileDatasetPostModel(**test_object)
    #     print(exc.exception)
    #     assert "Unsupported possible value" in str(exc.exception)

    # def test_pydantic_model_wrong_value_for_meta_data(self):
    #     """Test wrong fileending for cooler."""
    #     test_object = {
    #         "datasetName": "test",
    #         "description": "test-description",
    #         "assembly": "1",
    #         "cellCycleStage": "asynchronous",
    #         "perturbation": "No perturbation",
    #         "public": "false",
    #         "ValueType": "Interaction",
    #         "Method": "microC",  # This should not be possible
    #         "Normalization": "ICCF",
    #         "filetype": "cooler",
    #         "filename": "test.mcool",
    #         "sizeType": ''
    #     }
    #     with self.assertRaises(ValidationError) as exc:
    #         data_ojb = FileDatasetPostModel(**test_object)
    #     print(exc.exception)
    #     assert "Unsupported possible value" in str(exc.exception)
# TODO: this functionality was apparently removed from pydantic. check whether still needed
    # def test_reverse_alias(self):
    #     """Test if the reverse alias is working."""
    #     test_object = {
    #         "datasetName": "test",
    #         "description": "null",
    #         "assembly": "1",
    #         "cellCycleStage": "asynchronous",
    #         "perturbation": "No perturbation",
    #         "public": "false",
    #         "ValueType": "Interaction",
    #         "Method": "HiC",
    #         "Normalization": "ICCF",
    #         "filetype": "cooler",
    #         "filename": "test.mcool",
    #         "sizeType": ''
    #     }
    #     data_ojb = FileDatasetPostModel(**test_object)
    #     assert data_ojb["Normalization"] == data_ojb["normalization"]
    #     assert data_ojb["Normalization"] == "ICCF"


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
#             "cellCycleStage": "asynchronous",
#             "perturbation": "No perturbation",
#             "public": False,
#             "valueType": "GenomeAnnotation",
#             "method": "undefined",
#             "normalization": "undefined",
#             "filetype": "bedfile",
#             "processing_state": None,
#             "protein": "undefined",
#             "directionality": "+",
#             "derivationType": "undefined",
#             "sizeType": "Point",
#             "user_id": None,
#             "source_url": "http://thisisbed.bed"
#         }
#         data_ojb = URLDatasetPostModel(**test_object)
#         self.assertEqual(expected_object, data_ojb.dict())

if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
