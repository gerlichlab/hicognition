import os
import pandas as pd
import unittest
import json
import numpy as np
from test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
import sys

sys.path.append("./")
from app import db
from app.models import Dataset, Intervals, IndividualIntervalData, BedFileMetadata


class TestGetIndividualIntervalData(LoginTestCase, TempDirTestCase):
    """Test to check whether retrieving of individualIntervalData data
    works."""

    def setUp(self):
        super().setUp()
        # add unowned bigwig
        self.unowned_bigwig = Dataset(id=1, filetype="bigwig", user_id=5)
        # add owned bigwig
        self.owned_bigwig = Dataset(id=2, filetype="bigwig", user_id=1)
        # add owned bedfile
        self.owned_bedfile = Dataset(id=3, filetype="bedfile", user_id=1)
        # add unowned bedfile
        self.unowned_bedfile = Dataset(id=4, filetype="bedfile", user_id=2)
        # add unowned, public bigwig
        self.unowned_public_bigwig = Dataset(
            id=5, filetype="bigwig", user_id=5, public=True
        )
        self.unowned_public_bedfile = Dataset(
            id=6, filetype="bedfile", user_id=2, public=True
        )
        # add owned intervals
        self.owned_intervals = Intervals(
            id=1, dataset_id=self.owned_bedfile.id, windowsize=200000
        )
        # add not owned intervals
        self.unowned_intervals = Intervals(
            id=2, dataset_id=self.unowned_bedfile.id, windowsize=200000
        )
        # add not owned, public intervals
        self.unowned_public_intervals = Intervals(
            id=3, dataset_id=self.unowned_public_bedfile.id, windowsize=200000
        )
        # add individualIntervalData from unowned bigwig
        self.indData_unowned_bigwig = IndividualIntervalData(
            id=1,
            binsize=10000,
            dataset_id=self.unowned_bigwig.id,
            intervals_id=self.owned_intervals.id,
        )
        # add individualIntervalData from unowned intervals
        self.indData_unowned_intervals = IndividualIntervalData(
            id=1,
            binsize=10000,
            dataset_id=self.owned_bigwig.id,
            intervals_id=self.unowned_intervals.id,
        )
        # add individualIntervalData with owned intervals and bigwig
        self.ind_data = np.array([[1.66, 2.2, 3.8, 4.5]])
        data_path = os.path.join(TempDirTestCase.TEMP_PATH, "test.npy")
        np.save(data_path, self.ind_data)
        self.indData_owned = IndividualIntervalData(
            binsize=10000,
            file_path_small=data_path,
            dataset_id=self.owned_bigwig.id,
            intervals_id=self.owned_intervals.id,
        )
        # add individualIntervalData with owned intervals and bigwig and nans
        self.test_data_w_nans = np.array([[1.66, 2.2, 3.8, 4.5, np.nan]])
        data_path_w_nans = os.path.join(TempDirTestCase.TEMP_PATH, "test1.npy")
        np.save(data_path_w_nans, self.test_data_w_nans)
        self.indData_owned_w_nans = IndividualIntervalData(
            binsize=10000,
            file_path_small=data_path_w_nans,
            dataset_id=self.owned_bigwig.id,
            intervals_id=self.owned_intervals.id,
        )
        # add individualIntervalData with owned intervals and bigwig and nans
        self.test_data_w_inf = np.array([[1.66, 2.2, 3.8, 4.5, np.inf]])
        data_path_w_inf = os.path.join(TempDirTestCase.TEMP_PATH, "test2.npy")
        np.save(data_path_w_inf, self.test_data_w_inf)
        self.indData_owned_w_inf = IndividualIntervalData(
            binsize=10000,
            file_path_small=data_path_w_inf,
            dataset_id=self.owned_bigwig.id,
            intervals_id=self.owned_intervals.id,
        )
        # add public individualIntervalData
        self.indData_unowned_public = IndividualIntervalData(
            binsize=10000,
            file_path_small=data_path,
            dataset_id=self.unowned_public_bigwig.id,
            intervals_id=self.unowned_public_intervals.id,
        )

    def test_no_auth(self):
        """No authentication provided, response should be 401"""
        # protected route
        response = self.client.get(
            "/api/individualIntervalData/1/", content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

    def test_individualIntervalData_does_not_exist(self):
        """Test 404 is returned if individualIntervalData does not exist."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # make request
        response = self.client.get(
            "/api/individualIntervalData/500/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_bigwig_not_owned(self):
        """Bigwig dataset underlying individualIntervalData is not owned"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        db.session.add_all(
            [
                self.unowned_bigwig,
                self.owned_bedfile,
                self.owned_intervals,
                self.indData_unowned_bigwig,
            ]
        )
        db.session.commit()
        # make request
        response = self.client.get(
            f"/api/individualIntervalData/{self.indData_unowned_bigwig.id}/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_intervals_not_owned(self):
        """Intervals dataset underlying individualIntervalData is not owned"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        db.session.add_all(
            [
                self.owned_bigwig,
                self.unowned_bedfile,
                self.unowned_intervals,
                self.indData_unowned_intervals,
            ]
        )
        db.session.commit()
        # make request for bigwig with forbidden interval
        response = self.client.get(
            f"/api/individualIntervalData/{self.indData_unowned_intervals.id}/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_correct_data_returned(self):
        """Correct data is returned from an owned individualIntervalData"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        db.session.add_all(
            [
                self.owned_bigwig,
                self.owned_bedfile,
                self.owned_intervals,
                self.indData_owned,
            ]
        )
        db.session.commit()
        # make request
        response = self.client.get(
            f"/api/individualIntervalData/{self.indData_owned.id}/",
            headers=token_headers,
            content_type="application/json",
        )
        expected = {
            "data": self.ind_data.flatten().tolist(),
            "shape": list(self.ind_data.shape),
            "dtype": "float32",
        }
        self.assertEqual(response.json, expected)

    def test_correct_data_returned_w_nan(self):
        """Correct data is returned from an owned individualIntervalData that contains nan"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        db.session.add_all(
            [
                self.owned_bigwig,
                self.owned_bedfile,
                self.owned_intervals,
                self.indData_owned_w_nans,
            ]
        )
        db.session.commit()
        # make request
        response = self.client.get(
            f"/api/individualIntervalData/{self.indData_owned_w_nans.id}/",
            headers=token_headers,
            content_type="application/json",
        )
        expected = {
            "data": [
                i if not np.isnan(i) else None for i in self.test_data_w_nans.flatten()
            ],
            "shape": list(self.test_data_w_nans.shape),
            "dtype": "float32",
        }
        self.assertEqual(response.json, expected)

    def test_correct_data_returned_w_inf(self):
        """Correct data is returned from an owned individualIntervalData that contains nan"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        db.session.add_all(
            [
                self.owned_bigwig,
                self.owned_bedfile,
                self.owned_intervals,
                self.indData_owned_w_inf,
            ]
        )
        db.session.commit()
        # make request
        response = self.client.get(
            f"/api/individualIntervalData/{self.indData_owned_w_inf.id}/",
            headers=token_headers,
            content_type="application/json",
        )
        expected = {
            "data": [
                i if not np.isinf(i) else None for i in self.test_data_w_inf.flatten()
            ],
            "shape": list(self.test_data_w_inf.shape),
            "dtype": "float32",
        }
        self.assertEqual(response.json, expected)

    def test_public_unowned_data_returned(self):
        """Test whether public, unowned data is returned correctly."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        db.session.add_all(
            [
                self.unowned_public_bigwig,
                self.unowned_public_bedfile,
                self.unowned_public_intervals,
                self.indData_unowned_public,
            ]
        )
        db.session.commit()
        # make request
        response = self.client.get(
            f"/api/individualIntervalData/{self.indData_unowned_public.id}/",
            headers=token_headers,
            content_type="application/json",
        )
        expected = {
            "data": self.ind_data.flatten().tolist(),
            "shape": list(self.ind_data.shape),
            "dtype": "float32",
        }
        self.assertEqual(response.json, expected)


class TestGetStackupMetadata(LoginTestCase, TempDirTestCase):
    """Tests for /individualIntervalData/<stackup_id>/metadatasmall"""

    def setUp(self):
        super().setUp()
        # add unowned bigwig
        self.unowned_bigwig = Dataset(id=1, filetype="bigwig", user_id=5)
        # add owned bigwig
        self.owned_bigwig = Dataset(id=2, filetype="bigwig", user_id=1)
        # add owned bedfile
        self.owned_bedfile = Dataset(id=3, filetype="bedfile", user_id=1)
        # add unowned bedfile
        self.unowned_bedfile = Dataset(id=4, filetype="bedfile", user_id=2)
        # add owned intervals
        self.indices_1 = np.array([0, 2])
        index_file = os.path.join(TempDirTestCase.TEMP_PATH, "indices.npy")
        np.save(index_file, self.indices_1)
        self.owned_intervals = Intervals(
            id=1,
            dataset_id=self.owned_bedfile.id,
            file_path_sub_sample_index=index_file,
            windowsize=200000,
        )
        # add not owned intervals
        self.unowned_intervals = Intervals(
            id=2, dataset_id=self.unowned_bedfile.id, windowsize=200000
        )
        # add individualIntervalData from unowned bigwig
        self.indData_unowned_bigwig = IndividualIntervalData(
            id=1,
            binsize=10000,
            dataset_id=self.unowned_bigwig.id,
            intervals_id=self.owned_intervals.id,
        )
        # add individualIntervalData from unowned intervals
        self.indData_unowned_intervals = IndividualIntervalData(
            id=1,
            binsize=10000,
            dataset_id=self.owned_bigwig.id,
            intervals_id=self.unowned_intervals.id,
        )
        # add owned individualIntervalData
        self.indData_owned = IndividualIntervalData(
            binsize=10000,
            dataset_id=self.owned_bigwig.id,
            intervals_id=self.owned_intervals.id,
        )
        # add metadata without file and fields
        self.metadata_wo_fields = BedFileMetadata(dataset_id=self.owned_bedfile.id)
        # add metadata with file and fields
        metadata_file_path_1 = os.path.join(TempDirTestCase.TEMP_PATH, "test.csv")
        self.metadata_1_df = pd.DataFrame(
            {"id": [0, 1, 2, 3, 4, 5], "start": [0] * 6, "end": [10] * 6}
        )
        self.metadata_1_df.to_csv(metadata_file_path_1, index=False)
        self.metadata_1 = BedFileMetadata(
            file_path=metadata_file_path_1,
            metadata_fields='["id", "start"]',
            dataset_id=self.owned_bedfile.id,
        )
        # add metadata with file without fields
        metadata_file_path_2 = os.path.join(TempDirTestCase.TEMP_PATH, "test2.csv")
        self.metadata_2_df = pd.DataFrame({"end": [10] * 6})
        self.metadata_2_df.to_csv(metadata_file_path_2, index=False)
        self.metadata_w_file_wo_fields = BedFileMetadata(
            file_path=metadata_file_path_2, dataset_id=self.owned_bedfile.id
        )
        # add metadata with file with fields number 2
        self.metadata_2 = BedFileMetadata(
            file_path=metadata_file_path_2,
            metadata_fields='["end"]',
            dataset_id=self.owned_bedfile.id,
        )

    def test_no_auth(self):
        """No authentication provided, response should be 401"""
        # protected route
        response = self.client.get(
            "/api/individualIntervalData/1/metadatasmall",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

    def test_individualIntervalData_does_not_exist(self):
        """Test 404 is returned if individualIntervalData does not exist."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # make request
        response = self.client.get(
            "/api/individualIntervalData/500/metadatasmall",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_bigwig_not_owned(self):
        """Bigwig dataset underlying individualIntervalData is not owned"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        db.session.add_all(
            [
                self.unowned_bigwig,
                self.owned_bedfile,
                self.owned_intervals,
                self.indData_unowned_bigwig,
            ]
        )
        db.session.commit()
        # make request
        response = self.client.get(
            f"/api/individualIntervalData/{self.indData_unowned_bigwig.id}/metadatasmall",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_intervals_not_owned(self):
        """Intervals dataset underlying individualIntervalData is not owned"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        db.session.add_all(
            [
                self.owned_bigwig,
                self.unowned_bedfile,
                self.unowned_intervals,
                self.indData_unowned_intervals,
            ]
        )
        db.session.commit()
        # make request for bigwig with forbidden interval
        response = self.client.get(
            f"/api/individualIntervalData/{self.indData_unowned_intervals.id}/metadatasmall",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_empty_response_no_metadata(self):
        """Tests whether empty response is returned when there are no associated metadata"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        db.session.add_all(
            [
                self.owned_bigwig,
                self.owned_bedfile,
                self.owned_intervals,
                self.indData_owned,
            ]
        )
        db.session.commit()
        # make request
        response = self.client.get(
            f"/api/individualIntervalData/{self.indData_owned.id}/metadatasmall",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.json, {})

    def test_empty_response_metadata_without_fields(self):
        """Tests whether empty response is returned when associated
        metadata fields are empty."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        db.session.add_all(
            [
                self.owned_bigwig,
                self.owned_bedfile,
                self.owned_intervals,
                self.indData_owned,
                self.metadata_wo_fields,
            ]
        )
        db.session.commit()
        # make request
        response = self.client.get(
            f"/api/individualIntervalData/{self.indData_owned.id}/metadatasmall",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.json, {})

    def test_good_single_metadata_entry_is_returned_correctly(self):
        """Tests whether single associated metadata entry to
        small stackup file is returned correctly, meaning the
        corresponding indices are returned."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        db.session.add_all(
            [
                self.owned_bigwig,
                self.owned_bedfile,
                self.owned_intervals,
                self.indData_owned,
                self.metadata_1,
            ]
        )
        db.session.commit()
        # make apicall
        response = self.client.get(
            f"/api/individualIntervalData/{self.indData_owned.id}/metadatasmall",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            self.metadata_1_df.loc[
                :, json.loads(self.metadata_1.metadata_fields)
            ]  # select fields
            .iloc[self.indices_1, :]  # select indices
            .to_dict(orient="list"),  # convert to json
        )

    def test_entries_with_no_fields_specified_are_not_returned(self):
        """Tests whether associated metadata fiels with no field names
        specified are not returned"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        db.session.add_all(
            [
                self.owned_bigwig,
                self.owned_bedfile,
                self.owned_intervals,
                self.indData_owned,
                self.metadata_1,
                self.metadata_w_file_wo_fields,
            ]
        )
        db.session.commit()
        # make apicall
        response = self.client.get(
            f"/api/individualIntervalData/{self.indData_owned.id}/metadatasmall",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            self.metadata_1_df.loc[
                :, json.loads(self.metadata_1.metadata_fields)
            ]  # select fields
            .iloc[self.indices_1, :]  # select indices
            .to_dict(orient="list"),  # convert to json
        )

    def test_metadata_entries_with_overlapping_fieldname_are_returned_correctly(self):
        """Tests whether multiple associated metadata entries to
        interval file with overlapping fieldnames returned the newest field (by larger id value)"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # generate mock datasets in temp-directory
        db.session.add_all(
            [
                self.owned_bigwig,
                self.owned_bedfile,
                self.owned_intervals,
                self.indData_owned,
                self.metadata_1,
                self.metadata_2,
            ]
        )
        db.session.commit()
        # make apicall
        response = self.client.get(
            f"/api/individualIntervalData/{self.indData_owned.id}/metadatasmall",
            headers=token_headers,
            content_type="application/json",
        )
        # construct expected
        expected = self.metadata_1_df
        expected.loc[:, "end"] = self.metadata_2_df[
            "end"
        ]  # add info from second metadata entry
        expected = expected.iloc[
            self.indices_1, :
        ]  # subset on the subsample indices defined in the interval file
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), expected.to_dict(orient="list"))


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
