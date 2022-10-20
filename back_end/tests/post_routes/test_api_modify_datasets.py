"""Module with tests realted to managing and modifying datasets."""
import logging
import unittest
from hicognition.test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
# import sys
# sys.path.append("./")
from app.models import Dataset, Assembly
from app import db


class TestModifyDatasets(LoginTestCase, TempDirTestCase):
    """Tests correct modification of datasets"""

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
        # create field form mapping
        self.field_form_mapping = {
            "datasetName": "dataset_name",
            "cellCycleStage": "cellCycleStage",
            "perturbation": "perturbation",
            "ValueType": "valueType",
            "Method": "method",
            "Normalization": "normalization",
            "DerivationType": "derivationType",
            "Protein": "protein",
            "Directionality": "directionality",
            "public": "public",
        }
        # add token headers
        token = self.add_and_authenticate("test", "asdf")
        # create token_header
        self.token_headers = self.get_token_header(token)
        # add content-type
        self.token_headers["Content-Type"] = "multipart/form-data"
        # create datasets
        self.owned_cooler_1 = self.create_dataset(
            id=1,
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="cooler",
            processing_state="finished",
            user_id=1,
            assembly=1,
        )
        self.bedfile_1 = self.create_dataset(
            id=2,
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="bedfile",
            processing_state="finished",
            user_id=1,
            assembly=1,
        )
        self.bedfile_2 = self.create_dataset(
            id=3,
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="bedfile",
            processing_state="finished",
            user_id=1,
            assembly=1,
        )
        self.bigwig_1 = self.create_dataset(
            id=4,
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="bigwig",
            processing_state="finished",
            user_id=1,
            assembly=1,
        )
        # add unowned coolers
        self.unowned_cooler = self.create_dataset(
            id=4,
            dataset_name="test2",
            file_path="/test/path/2",
            filetype="cooler",
            processing_state="finished",
            user_id=2,
        )

    def test_no_auth(self):
        """No authentication provided, response should be 401"""
        # protected route
        response = self.client.put("/api/datasets/1/", content_type="application/json")
        self.assertEqual(response.status_code, 401)

    def test_dataset_does_not_exist(self):
        """Tests whether 404 is returned when dataset does not exist."""
        # put datasets
        data = {
            "datasetName": "changedName",
            "cellCycleStage": "changedCellCycleStage",
            "perturbation": "hangedPerturbation",
            "ValueType": "Interaction",
            "public": "false",
            "Method": "HiC",
            "Normalization": "ICCF",
        }
        response = self.client.put(
            "/api/datasets/500/",
            data = data,
            headers=self.token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 404)

    def test_dataset_not_owned(self):
        """Tests whether 403 is returned when dataset is not owned"""
        # add datasets
        db.session.add(self.unowned_cooler)
        db.session.commit()
        data = {
            "datasetName": "changedName",
            "cellCycleStage": "changedCellCycleStage",
            "perturbation": "hangedPerturbation",
            "ValueType": "Interaction",
            "public": "false",
            "Method": "HiC",
            "Normalization": "ICCF",
        }
        # put datasets
        response = self.client.put(
            f"/api/datasets/{self.unowned_cooler.id}/",
            data=data,
            headers=self.token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 403)

    def test_badform_no_form(self):
        """Test 400 returned if no form is provided."""
        # add datasets
        db.session.add(self.owned_cooler_1)
        db.session.commit()
        # put datasets
        response = self.client.put(
            f"/api/datasets/{self.owned_cooler_1.id}/",
            headers=self.token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    # removed, does not make sense anymore
    # def test_badform_no_common_required_keys(self):
    #     """Test 400 returned if no form is provided."""
    #     # add datasets
    #     db.session.add(self.owned_cooler_1)
    #     db.session.commit()
    #     # construct form
    #     data = {"Method": "HiC", "Normalization": "ICCF", "public": "false"}
    #     # put datasets
    #     response = self.client.put(
    #         f"/api/datasets/{self.owned_cooler_1.id}/",
    #         headers=self.token_headers,
    #         data=data,
    #         content_type="multipart/form-data",
    #     )
    #     self.assertEqual(response.status_code, 400)

    # is allowed now
    # def test_badform_no_metdata(self):
    #     """Test 400 returned if no form is provided."""
    #     # add datasets
    #     db.session.add(self.owned_cooler_1)
    #     db.session.commit()
    #     # construct form
    #     data = {
    #         "datasetName": "test",
    #         "cellCycleStage": "asynchronous",
    #         "perturbation": "No perturbation",
    #         "ValueType": "Interaction",
    #         "public": "false",
    #     }
    #     # put datasets
    #     response = self.client.put(
    #         f"/api/datasets/{self.owned_cooler_1.id}/",
    #         headers=self.token_headers,
    #         data=data,
    #         content_type="multipart/form-data",
    #     )
    #     self.assertEqual(response.status_code, 400)

    def test_badform_incorrect_valuetype(self):
        """Test 400 returned if no form is provided."""
        # add datasets
        db.session.add(self.owned_cooler_1)
        db.session.commit()
        # construct form
        data = {
            "datasetName": "test",
            "cellCycleStage": "asynchronous",
            "perturbation": "No perturbation",
            "ValueType": "Interaction",
            "Method": "HiC",
            "public": "false",
            "Normalization": "ICCF",
            "assembly": 1,
        }
        # put datasets
        response = self.client.put(
            f"/api/datasets/{self.owned_cooler_1.id}/",
            headers=self.token_headers,
            data=data,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    def test_badform_contains_assembly(self):
        """Test 400 returned if no form is provided."""
        # add datasets
        db.session.add(self.owned_cooler_1)
        db.session.commit()
        # put datasets
        response = self.client.put(
            f"/api/datasets/{self.owned_cooler_1.id}/",
            headers=self.token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    def test_badform_contains_sizetype(self):
        """Test 400 returned if no form is provided."""
        # add datasets
        db.session.add(self.owned_cooler_1)
        db.session.commit()
        # construct form
        data = {
            "datasetName": "test",
            "cellCycleStage": "asynchronous",
            "perturbation": "No perturbation",
            "ValueType": "Interaction",
            "public": "false",
            "Method": "HiC",
            "Normalization": "ICCF",
            "SizeType": "IEE",
        }
        # put datasets
        response = self.client.put(
            f"/api/datasets/{self.owned_cooler_1.id}/",
            headers=self.token_headers,
            data=data,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    def test_modification_goes_through_cooler(self):
        """Test whether correct combination of metadata causes database modifiction."""
        # add datasets
        db.session.add(self.owned_cooler_1)
        db.session.commit()
        # construct form
        data = {
            "datasetName": "changedName",
            "cellCycleStage": "changedCellCycleStage",
            "perturbation": "hangedPerturbation",
            "ValueType": "Interaction",
            "public": "false",
            "Method": "HiC",
            "Normalization": "ICCF",
        }
        # put datasets
        response = self.client.put(
            f"/api/datasets/{self.owned_cooler_1.id}/",
            headers=self.token_headers,
            data=data,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        # check whether modificaiton fields were modified
        dataset = Dataset.query.get(self.owned_cooler_1.id)
        for field in data.keys():
            if field == "public":
                self.assertEqual(
                    dataset.__getattribute__(self.field_form_mapping[field]), False
                )
            else:
                self.assertEqual(
                    dataset.__getattribute__(self.field_form_mapping[field]),
                    data[field],
                )
        # check whether fields that should be undefined are undefined
        for field in ["protein", "directionality", "derivationType"]:
            self.assertEqual(dataset.__getattribute__(field), "undefined")
        # check whether assembly and filetype are unchanged
        self.assertEqual(dataset.assembly, 1)
        self.assertEqual(dataset.filetype, "cooler")

    def test_modification_goes_through_bedfile(self):
        """Test whether correct combination of metadata causes database modifiction."""
        # add datasets
        db.session.add(self.bedfile_1)
        db.session.commit()
        # construct form data
        data = {
            "datasetName": "test",
            "cellCycleStage": "asynchronous",
            "perturbation": "No perturbation",
            "ValueType": "Derived",
            "public": "false",
            "Method": "HiC",
        }
        # put datasets
        response = self.client.put(
            f"/api/datasets/{self.bedfile_1.id}/",
            headers=self.token_headers,
            data=data,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        # check whether modificaiton fields were modified
        dataset = Dataset.query.get(self.bedfile_1.id)
        for field in data.keys():
            if field == "public":
                self.assertEqual(
                    dataset.__getattribute__(self.field_form_mapping[field]), False
                )
            else:
                self.assertEqual(
                    dataset.__getattribute__(self.field_form_mapping[field]),
                    data[field],
                )
        # check whether fields that should be undefined are undefined
        for field in ["protein", "directionality"]:
            self.assertEqual(dataset.__getattribute__(field), "undefined")
        # check whether assembly and filetype are unchanged
        self.assertEqual(dataset.assembly, 1)
        self.assertEqual(dataset.filetype, "bedfile")

    def test_modification_goes_through_bedfile_genome_annotation(self):
        """Test whether correct combination of metadata causes database modifiction."""
        # add datasets
        db.session.add(self.bedfile_2)
        db.session.commit()
        # construct form data
        data = {
            "datasetName": "fdsa",
            "ValueType": "GenomeAnnotation",
            "Directionality": "No directionality",
            "cellCycleStage": "none",
            "public": "false",
            "perturbation": "none",
        }
        # put datasets
        response = self.client.put(
            f"/api/datasets/{self.bedfile_2.id}/",
            headers=self.token_headers,
            data=data,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        # check whether modificaiton fields were modified
        dataset = Dataset.query.get(self.bedfile_2.id)
        for field in data.keys():
            if field == "public":
                self.assertEqual(
                    dataset.__getattribute__(self.field_form_mapping[field]), False
                )
            else:
                self.assertEqual(
                    dataset.__getattribute__(self.field_form_mapping[field]),
                    data[field],
                )
        # check whether assembly and filetype are unchanged
        self.assertEqual(dataset.assembly, 1)
        self.assertEqual(dataset.filetype, "bedfile")

    def test_public_flag_set_correctly(self):
        """Test if public flag is set correctly."""
        # add datasets
        db.session.add(self.bedfile_2)
        db.session.commit()
        # construct form data
        data = {
            "datasetName": "fdsa",
            "ValueType": "GenomeAnnotation",
            "Directionality": "No directionality",
            "cellCycleStage": "none",
            "perturbation": "none",
            "public": "true",
        }
        # put datasets
        response = self.client.put(
            f"/api/datasets/{self.bedfile_2.id}/",
            headers=self.token_headers,
            data=data,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        # check whether modificaiton fields were modified
        dataset = Dataset.query.get(self.bedfile_2.id)
        for field in data.keys():
            if field == "public":
                self.assertEqual(
                    dataset.__getattribute__(self.field_form_mapping[field]), True
                )
            else:
                self.assertEqual(
                    dataset.__getattribute__(self.field_form_mapping[field]),
                    data[field],
                )
        # check whether assembly and filetype are unchanged
        self.assertEqual(dataset.assembly, 1)
        self.assertEqual(dataset.filetype, "bedfile")

    def test_modification_goes_through_bigwig(self):
        """Test whether correct combination of metadata causes database modifiction."""
        # add datasets
        db.session.add(self.bigwig_1)
        db.session.commit()
        # construct form data
        data = {
            "datasetName": "test",
            "cellCycleStage": "asynchronous",
            "perturbation": "No perturbation",
            "ValueType": "ChromatinAssociation",
            "Protein": "CTCF",
            "Method": "ChipSeq",
            "public": "false",
            "Normalization": "RPM",
        }
        # put datasets
        response = self.client.put(
            f"/api/datasets/{self.bigwig_1.id}/",
            headers=self.token_headers,
            data=data,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        # check whether modificaiton fields were modified
        dataset = Dataset.query.get(self.bigwig_1.id)
        for field in data.keys():
            if field == "public":
                self.assertEqual(
                    dataset.__getattribute__(self.field_form_mapping[field]), False
                )
            else:
                self.assertEqual(
                    dataset.__getattribute__(self.field_form_mapping[field]),
                    data[field],
                )
        # check whether fields that should be undefined are undefined
        for field in ["derivationType", "directionality"]:
            self.assertEqual(dataset.__getattribute__(field), "undefined")
        # check whether assembly and filetype are unchanged
        self.assertEqual(dataset.assembly, 1)
        self.assertEqual(dataset.filetype, "bigwig")


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
