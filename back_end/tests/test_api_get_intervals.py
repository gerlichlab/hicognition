import unittest
import os
import json
import pandas as pd
from test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
import sys

sys.path.append("./")
from app import db
from app.models import Dataset, Intervals, BedFileMetadata, Session


class TestGetIntervals(LoginTestCase):
    """Tests for /api/intervals route to list
    intervals."""

    def setUp(self):
        super().setUp()
        # add owned dataset
        self.owned_dataset = Dataset(
            id=1,
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="cooler",
            user_id=1,
        )
        # add unowned dataset
        self.unowned_dataset = Dataset(
            id=2,
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="cooler",
            user_id=2,
        )
        # add public dataset
        self.unowned_public_dataset = Dataset(
            id=3,
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="cooler",
            user_id=2,
            public=True,
        )
        # add intervals for owned dataset
        self.owned_intervals_1 = Intervals(
            id=1,
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            windowsize=200000,
        )
        self.owned_intervals_2 = Intervals(
            id=2,
            name="testRegion2",
            dataset_id=1,
            file_path="test_path_2.bedd2db",
            windowsize=400000,
        )
        # add intervals for unowned dataset
        self.unowned_intervals = Intervals(
            id=3,
            name="testRegion3",
            dataset_id=2,
            file_path="test_path_3.bedd2db",
            windowsize=400000,
        )
        # add intervals for public dataset
        self.public_intervals = Intervals(
            id=4,
            name="testRegion3",
            dataset_id=3,
            file_path="test_path_3.bedd2db",
            windowsize=400000,
        )
        # add session for unowned dataset
        self.session_unowned_dataset = Session(datasets=[self.unowned_dataset])
        # add groupings
        self.owned_dataset_intervals = [
            self.owned_dataset,
            self.owned_intervals_1,
            self.owned_intervals_2,
        ]
        self.unowned_dataset_intervals = [self.unowned_dataset, self.unowned_intervals]
        self.all_standard_intervals = [
            self.owned_intervals_1,
            self.owned_intervals_2,
            self.unowned_intervals,
        ]

    def test_no_auth(self):
        """No authentication provided, response should be 401"""
        # protected route
        response = self.client.get("/api/intervals/", content_type="application/json")
        self.assertEqual(response.status_code, 401)

    def test_correct_intervals_single_dataset(self):
        """Correct intervals are returned for single dataset."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        db.session.add_all(self.owned_dataset_intervals)
        db.session.commit()
        # get intervals
        response = self.client.get(
            "/api/intervals/",
            headers=token_headers,
            content_type="application/json",
        )
        # check whether they are correct
        expected = [self.owned_intervals_1.to_json(), self.owned_intervals_2.to_json()]
        self.assertEqual(response.json, expected)

    def test_correct_intervals_two_datasets(self):
        """Tests whether correct intervals are returned if
        there are multiple datasets from different users."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        db.session.add_all(
            [*self.owned_dataset_intervals, *self.unowned_dataset_intervals]
        )
        db.session.commit()
        # get intervals
        response = self.client.get(
            "/api/intervals/",
            headers=token_headers,
            content_type="application/json",
        )
        # check whether they are correct
        expected = [self.owned_intervals_1.to_json(), self.owned_intervals_2.to_json()]
        self.assertEqual(response.json, expected)

    def test_correct_intervals_with_valid_session_token(self):
        """Tests whether correct intervals are returned if
        there are multiple datasets from different users and
        there is a valid session token."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        db.session.add_all(
            [
                *self.owned_dataset_intervals,
                *self.unowned_dataset_intervals,
                self.session_unowned_dataset,
            ]
        )
        db.session.commit()
        # get intervals
        token = self.session_unowned_dataset.generate_session_token()
        response = self.client.get(
            f"/api/intervals/?sessionToken={token}",
            headers=token_headers,
            content_type="application/json",
        )
        # check whether they are correct
        expected = [dataset.to_json() for dataset in self.all_standard_intervals]
        self.assertEqual(response.json, expected)

    def test_get_public_intervals(self):
        """Tests whether intervals are returned for a public but not
        owned dataset."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        db.session.add_all([self.unowned_public_dataset, self.public_intervals])
        db.session.commit()
        # get intervals
        response = self.client.get(
            "/api/intervals/",
            headers=token_headers,
            content_type="application/json",
        )
        # check whether they are correct
        self.assertEqual(response.json, [self.public_intervals.to_json()])


class TestGetIntervalMetadata(LoginTestCase, TempDirTestCase):
    """Test-suite to test getting associated metadata."""

    def setUp(self):
        super().setUp()
        # add owned dataset
        self.owned_dataset = Dataset(
            id=1,
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="cooler",
            user_id=1,
        )
        # add unowned dataset
        self.unowned_dataset = Dataset(
            id=2,
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="cooler",
            user_id=2,
        )
        # add intetvals for owned dataset
        intervals_file_path = os.path.join(TempDirTestCase.TEMP_PATH, "test.bedpe")
        intervals_df = pd.DataFrame(
            {
                "chrom": ["chr1"] * 6,
                "start": [0] * 6,
                "end": [10] * 6,
                "bed_row_id": range(6),
            }
        )
        intervals_df.to_csv(intervals_file_path, index=False, header=None, sep="\t")
        self.owned_intervals = Intervals(
            id=1,
            name="testRegion1",
            dataset_id=1,
            file_path=intervals_file_path,
            windowsize=200000,
        )
        # add intervals for owned dataset with filtered rows
        intervals_filtered_file_path = os.path.join(
            TempDirTestCase.TEMP_PATH, "test_filtered.bedpe"
        )
        self.intervals_filtered_df = pd.DataFrame(
            {
                "chrom": ["chr1"] * 6,
                "start": [0] * 6,
                "end": [10] * 6,
                "bed_row_id": [0, 2, 4, 6, 8, 10],
            }
        )
        self.intervals_filtered_df.to_csv(
            intervals_filtered_file_path, index=False, header=None, sep="\t"
        )
        self.owned_intervals_filtered_rows = Intervals(
            id=2,
            name="testRegion1",
            dataset_id=1,
            file_path=intervals_filtered_file_path,
            windowsize=200000,
        )
        # add intervals for unowned dataset
        self.unowned_intervals = Intervals(
            id=3,
            name="testRegion1",
            dataset_id=2,
            file_path="test_path_1.bedd2db",
            windowsize=200000,
        )
        # add metadata 1 for owned dataset
        metadata_file_path_1 = os.path.join(TempDirTestCase.TEMP_PATH, "test.csv")
        self.metadata_df_simple_1 = pd.DataFrame(
            {"id": [0, 1, 2, 3, 4, 5], "start": [0] * 6, "end": [10] * 6}
        )
        self.metadata_df_simple_1.to_csv(metadata_file_path_1, index=False)
        self.metadata_simple_1 = BedFileMetadata(
            file_path=metadata_file_path_1,
            metadata_fields='["id", "start"]',
            dataset_id=1,
        )
        # add metadata 2 for owned dataset
        metadata_file_path_2 = os.path.join(TempDirTestCase.TEMP_PATH, "test2.csv")
        self.metadata_df_simple_2 = pd.DataFrame({"end": [10] * 6})
        self.metadata_df_simple_2.to_csv(metadata_file_path_2, index=False)
        self.metadata_simple_2 = BedFileMetadata(
            file_path=metadata_file_path_2, metadata_fields='["end"]', dataset_id=1
        )
        # add metadata 3 for owned dataset
        metadata_file_path_3 = os.path.join(TempDirTestCase.TEMP_PATH, "test3.csv")
        self.metadata_df_simple_3 = pd.DataFrame({"end": [12] * 6})
        self.metadata_df_simple_3.to_csv(metadata_file_path_3, index=False)
        self.metadata_simple_3 = BedFileMetadata(
            file_path=metadata_file_path_3, metadata_fields='["end"]', dataset_id=1
        )
        # add metadata without specified field
        self.metadata_wo_fields = BedFileMetadata(
            file_path=metadata_file_path_2, dataset_id=1
        )
        # add metadata for filtered intervals
        metadata_filtered_file_path = os.path.join(
            TempDirTestCase.TEMP_PATH, "test4.csv"
        )
        self.metadata_filtered_df = pd.DataFrame(
            {"id": range(11), "start": range(11), "end": range(1, 12)}
        )
        self.metadata_filtered_df.to_csv(metadata_filtered_file_path, index=False)
        self.metadata_filtered = BedFileMetadata(
            file_path=metadata_filtered_file_path,
            metadata_fields='["id", "start", "end"]',
            dataset_id=1,
        )

    def test_no_auth(self):
        """No authentication provided, response should be 401"""
        # protected route
        response = self.client.get(
            "/api/intervals/1/metadata", content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

    def test_interval_dataset_not_owned(self):
        """Tests whether intervals associated with not owned dataset returns 403 error"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        db.session.add_all([self.unowned_dataset, self.unowned_intervals])
        db.session.commit()
        # get intervals
        response = self.client.get(
            f"/api/intervals/{self.unowned_intervals.id}/metadata",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_interval_id_does_not_exist(self):
        """Tests whether interval id that does not exist returns 404 error"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # get intervals
        response = self.client.get(
            "/api/intervals/500/metadata",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_no_metadata_returns_empty_response(self):
        """Tests whether empty response is returned if no metadata is associated with intervals"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        db.session.add_all([self.owned_dataset, self.owned_intervals])
        db.session.commit()
        # get intervals
        response = self.client.get(
            f"/api/intervals/{self.owned_intervals.id}/metadata",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {})

    def test_good_single_metadata_entry_is_returned_correctly(self):
        """Tests whether single associated metadata entry to
        interval file is returned correctly."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        db.session.add_all(
            [self.owned_dataset, self.owned_intervals, self.metadata_simple_1]
        )
        db.session.commit()
        # make apicall
        response = self.client.get(
            f"/api/intervals/{self.owned_intervals.id}/metadata",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            self.metadata_df_simple_1[
                json.loads(self.metadata_simple_1.metadata_fields)
            ].to_dict(orient="list"),
        )

    def test_good_metadata_entries_are_returned_correctly(self):
        """Tests whether multiple associated metadata entries to
        interval file is returned correctly."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        db.session.add_all(
            [
                self.owned_dataset,
                self.owned_intervals,
                self.metadata_simple_1,
                self.metadata_simple_2,
            ]
        )
        db.session.commit()
        # make apicall
        response = self.client.get(
            f"/api/intervals/{self.owned_intervals.id}/metadata",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(), self.metadata_df_simple_1.to_dict(orient="list")
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
                self.owned_dataset,
                self.owned_intervals,
                self.metadata_simple_1,
                self.metadata_wo_fields,
            ]
        )
        db.session.commit()
        # make apicall
        response = self.client.get(
            f"/api/intervals/{self.owned_intervals.id}/metadata",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            self.metadata_df_simple_1[
                json.loads(self.metadata_simple_1.metadata_fields)
            ].to_dict(orient="list"),
        )

    def test_metadata_entries_with_overlapping_fieldname_are_returned_correctly(self):
        """Tests whether multiple associated metadata entries to
        interval file with overlapping fieldnames returned the newest field (by larger id value)"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        db.session.add_all(
            [
                self.owned_dataset,
                self.owned_intervals,
                self.metadata_simple_1,
                self.metadata_simple_3,
            ]
        )
        db.session.commit()
        # make apicall
        response = self.client.get(
            f"/api/intervals/{self.owned_intervals.id}/metadata",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        expected = self.metadata_df_simple_1
        expected.loc[:, "end"] = self.metadata_df_simple_3["end"]
        self.assertEqual(response.get_json(), expected.to_dict(orient="list"))

    def test_metadata_entry_with_rows_differing_from_intervals_returned_correctly(self):
        """Context: A metadata file is associated with the bedfile and has an equal number
        of rows. However, the interval file that is associated with the bedfile does not necessarliy
        have the same number of rows because some intervals may be filtered out because the overlap
        chromosomal boundaries. This test checks whether such a case is handled correctly."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        db.session.add_all(
            [
                self.owned_dataset,
                self.owned_intervals_filtered_rows,
                self.metadata_filtered,
            ]
        )
        db.session.commit()
        # make apicall
        response = self.client.get(
            f"/api/intervals/{self.owned_intervals_filtered_rows.id}/metadata",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            self.metadata_filtered_df.iloc[
                self.intervals_filtered_df["bed_row_id"], :
            ].to_dict(orient="list"),
        )


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
