import unittest
import os
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
        dataset1 = Dataset(
            dataset_name="test1", file_path="/test/path/1", filetype="cooler", user_id=1
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            windowsize=200000,
        )
        intervals2 = Intervals(
            name="testRegion2",
            dataset_id=1,
            file_path="test_path_2.bedd2db",
            windowsize=400000,
        )
        db.session.add_all([dataset1, intervals1, intervals2])
        db.session.commit()
        # get intervals
        response = self.client.get(
            "/api/intervals/",
            headers=token_headers,
            content_type="application/json",
        )
        # check whether they are correct
        expected = [
            {
                "id": 1,
                "source_dataset": 1,
                "dataset_name": "testRegion1",
                "file_path": "test_path_1.bedd2db",
                "windowsize": 200000,
            },
            {
                "id": 2,
                "source_dataset": 1,
                "dataset_name": "testRegion2",
                "file_path": "test_path_2.bedd2db",
                "windowsize": 400000,
            },
        ]
        self.assertEqual(response.json, expected)

    def test_correct_intervals_two_datasets(self):
        """Tests whether correct intervals are returned if
        there are multiple datasets from different users."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token2 = self.add_and_authenticate("test2", "fdsa")
        # create token header
        token_headers = self.get_token_header(token)
        token_headers2 = self.get_token_header(token2)
        # add data
        dataset1 = Dataset(
            dataset_name="test1", file_path="/test/path/1", filetype="cooler", user_id=1
        )
        dataset2 = Dataset(
            dataset_name="test1", file_path="/test/path/1", filetype="cooler", user_id=2
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            windowsize=200000,
        )
        intervals2 = Intervals(
            name="testRegion2",
            dataset_id=1,
            file_path="test_path_2.bedd2db",
            windowsize=400000,
        )
        intervals3 = Intervals(
            name="testRegion3",
            dataset_id=2,
            file_path="test_path_3.bedd2db",
            windowsize=400000,
        )
        db.session.add_all([dataset1, dataset2, intervals1, intervals2, intervals3])
        db.session.commit()
        # get intervals
        response = self.client.get(
            "/api/intervals/",
            headers=token_headers,
            content_type="application/json",
        )
        # check whether they are correct
        expected = [
            {
                "id": 1,
                "source_dataset": 1,
                "dataset_name": "testRegion1",
                "file_path": "test_path_1.bedd2db",
                "windowsize": 200000,
            },
            {
                "id": 2,
                "source_dataset": 1,
                "dataset_name": "testRegion2",
                "file_path": "test_path_2.bedd2db",
                "windowsize": 400000,
            },
        ]
        self.assertEqual(response.json, expected)
        # test other user
        response = self.client.get(
            "/api/intervals/",
            headers=token_headers2,
            content_type="application/json",
        )
        # check whether they are correct
        expected = [
            {
                "id": 3,
                "source_dataset": 2,
                "dataset_name": "testRegion3",
                "file_path": "test_path_3.bedd2db",
                "windowsize": 400000,
            }
        ]
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
        dataset1 = Dataset(
            dataset_name="test1", file_path="/test/path/1", filetype="cooler", user_id=1
        )
        dataset2 = Dataset(
            dataset_name="test1", file_path="/test/path/1", filetype="cooler", user_id=2
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            windowsize=200000,
        )
        intervals2 = Intervals(
            name="testRegion2",
            dataset_id=1,
            file_path="test_path_2.bedd2db",
            windowsize=400000,
        )
        intervals3 = Intervals(
            name="testRegion3",
            dataset_id=2,
            file_path="test_path_3.bedd2db",
            windowsize=400000,
        )
        # add session
        session = Session()
        session.datasets = [dataset2]
        db.session.add_all([dataset1, dataset2, intervals1, intervals2, intervals3, session])
        db.session.commit()
        # get intervals
        token = session.generate_session_token()
        response = self.client.get(
            f"/api/intervals/?sessionToken={token}",
            headers=token_headers,
            content_type="application/json",
        )
        # check whether they are correct
        ids = [entry["id"] for entry in response.json]
        self.assertEqual(ids, [1,2,3])

    def test_get_public_intervals(self):
        """Tests whether intervals are returned for a public but not
        owned dataset."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token2 = self.add_and_authenticate("test2", "fdsa")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        dataset1 = Dataset(
            dataset_name="test1", file_path="/test/path/1", filetype="cooler", user_id=1
        )
        dataset2 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="cooler",
            public=True,
            user_id=2,
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            windowsize=200000,
        )
        intervals2 = Intervals(
            name="testRegion2",
            dataset_id=1,
            file_path="test_path_2.bedd2db",
            windowsize=400000,
        )
        intervals3 = Intervals(
            name="testRegion3",
            dataset_id=2,
            file_path="test_path_3.bedd2db",
            windowsize=400000,
        )
        db.session.add_all([dataset1, dataset2, intervals1, intervals2, intervals3])
        db.session.commit()
        # get intervals
        response = self.client.get(
            "/api/intervals/",
            headers=token_headers,
            content_type="application/json",
        )
        # check whether they are correct
        expected = [
            {
                "id": 1,
                "source_dataset": 1,
                "dataset_name": "testRegion1",
                "file_path": "test_path_1.bedd2db",
                "windowsize": 200000,
            },
            {
                "id": 2,
                "source_dataset": 1,
                "dataset_name": "testRegion2",
                "file_path": "test_path_2.bedd2db",
                "windowsize": 400000,
            },
            {
                "id": 3,
                "source_dataset": 2,
                "dataset_name": "testRegion3",
                "file_path": "test_path_3.bedd2db",
                "windowsize": 400000,
            },
        ]
        self.assertEqual(response.json, expected)


class TestGetSpecificIntervals(LoginTestCase):
    """Tests getting intervals of a specific dataset."""

    def test_no_auth(self):
        """No authentication provided, response should be 401"""
        # protected route
        response = self.client.get(
            "/api/datasets/1/intervals/", content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

    def test_404_if_wrong_id(self):
        """Tests whether status_code 404 is returned
        if id is wrong."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # get intervals
        response = self.client.get(
            "/api/datasets/500/intervals/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_403_if_not_owned_dataset(self):
        """Tests whether status_code 403 is returned
        if dataset is not owned."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token2 = self.add_and_authenticate("test2", "fdsa")
        # create token header
        token_headers2 = self.get_token_header(token2)
        # add data
        dataset1 = Dataset(
            dataset_name="test1", file_path="/test/path/1", filetype="cooler", user_id=1
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            windowsize=200000,
        )
        db.session.add_all([dataset1, intervals1])
        db.session.commit()
        # get intervals
        response = self.client.get(
            "/api/datasets/1/intervals/",
            headers=token_headers2,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_correct_intervals_returned(self):
        """Test whether only intervals belonging
        to a particular dataset are returned."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        dataset1 = Dataset(
            dataset_name="test1", file_path="/test/path/1", filetype="cooler", user_id=1
        )
        dataset2 = Dataset(
            dataset_name="test1", file_path="/test/path/1", filetype="cooler", user_id=1
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            windowsize=200000,
        )
        intervals2 = Intervals(
            name="testRegion2",
            dataset_id=1,
            file_path="test_path_2.bedd2db",
            windowsize=400000,
        )
        intervals3 = Intervals(
            name="testRegion3",
            dataset_id=2,
            file_path="test_path_3.bedd2db",
            windowsize=400000,
        )
        db.session.add_all([dataset1, dataset2, intervals1, intervals2, intervals3])
        db.session.commit()
        # get intervals
        response = self.client.get(
            "/api/datasets/1/intervals/",
            headers=token_headers,
            content_type="application/json",
        )
        # compare response
        expected = [
            {
                "id": 1,
                "source_dataset": 1,
                "dataset_name": "testRegion1",
                "file_path": "test_path_1.bedd2db",
                "windowsize": 200000,
            },
            {
                "id": 2,
                "source_dataset": 1,
                "dataset_name": "testRegion2",
                "file_path": "test_path_2.bedd2db",
                "windowsize": 400000,
            },
        ]
        self.assertEqual(response.json, expected)

    def test_access_to_public_but_unowned_intervals(self):
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add data
        dataset1 = Dataset(
            dataset_name="test1", file_path="/test/path/1", filetype="cooler", user_id=1
        )
        dataset2 = Dataset(
            dataset_name="test2",
            file_path="/test/path/2",
            filetype="cooler",
            public=True,
            user_id=2,
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            windowsize=200000,
        )
        intervals2 = Intervals(
            name="testRegion2",
            dataset_id=1,
            file_path="test_path_2.bedd2db",
            windowsize=400000,
        )
        intervals3 = Intervals(
            name="testRegion3",
            dataset_id=2,
            file_path="test_path_3.bedd2db",
            windowsize=400000,
        )
        db.session.add_all([dataset1, dataset2, intervals1, intervals2, intervals3])
        db.session.commit()
        # get intervals
        response = self.client.get(
            "/api/datasets/2/intervals/",
            headers=token_headers,
            content_type="application/json",
        )
        # compare response
        expected = [
            {
                "id": 3,
                "source_dataset": 2,
                "dataset_name": "testRegion3",
                "file_path": "test_path_3.bedd2db",
                "windowsize": 400000,
            }
        ]
        self.assertEqual(response.json, expected)


class TestGetIntervalMetadata(LoginTestCase, TempDirTestCase):
    """Test-suite to test getting associated metadata."""

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
        token2 = self.add_and_authenticate("test2", "fdsa")
        # create token header
        token_headers2 = self.get_token_header(token2)
        # add data
        dataset1 = Dataset(
            dataset_name="test1", file_path="/test/path/1", filetype="cooler", user_id=1
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            windowsize=200000,
        )
        db.session.add_all([dataset1, intervals1])
        db.session.commit()
        # get intervals
        response = self.client.get(
            "/api/intervals/1/metadata",
            headers=token_headers2,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_interval_id_does_not_exist(self):
        """Tests whether interval id that does not exist returns 404 error"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers2 = self.get_token_header(token)
        # add data
        dataset1 = Dataset(
            dataset_name="test1", file_path="/test/path/1", filetype="cooler", user_id=1
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            windowsize=200000,
        )
        db.session.add_all([dataset1, intervals1])
        db.session.commit()
        # get intervals
        response = self.client.get(
            "/api/intervals/500/metadata",
            headers=token_headers2,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_no_metadata_returns_empty_response(self):
        """Tests whether empty response is returned if no metadata is associated with intervals"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers2 = self.get_token_header(token)
        # add data
        dataset1 = Dataset(
            dataset_name="test1", file_path="/test/path/1", filetype="cooler", user_id=1
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=1,
            file_path="test_path_1.bedd2db",
            windowsize=200000,
        )
        db.session.add_all([dataset1, intervals1])
        db.session.commit()
        # get intervals
        response = self.client.get(
            "/api/intervals/1/metadata",
            headers=token_headers2,
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
        token_headers2 = self.get_token_header(token)
        # generate mock intervals in temp-directory
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
        # generate mock datasets in temp-directory
        metadata_file_path = os.path.join(TempDirTestCase.TEMP_PATH, "test.csv")
        metadata_df = pd.DataFrame(
            {"id": [0, 1, 2, 3, 4, 5], "start": [0] * 6, "end": [10] * 6}
        )
        metadata_df.to_csv(metadata_file_path, index=False)
        # add data
        dataset1 = Dataset(
            dataset_name="test1", file_path="/test/path/1", filetype="cooler", user_id=1
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=1,
            file_path=intervals_file_path,
            windowsize=200000,
        )
        metadata1 = BedFileMetadata(
            file_path=metadata_file_path,
            metadata_fields='["id", "start"]',
            dataset_id=1,
        )
        db.session.add_all([dataset1, intervals1, metadata1])
        db.session.commit()
        # make apicall
        response = self.client.get(
            "/api/intervals/1/metadata",
            headers=token_headers2,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            metadata_df.drop("end", axis="columns").to_dict(orient="list"),
        )

    def test_good_metadata_entries_are_returned_correctly(self):
        """Tests whether multiple associated metadata entries to
        interval file is returned correctly."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers2 = self.get_token_header(token)
        # generate mock intervals in temp-directory
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
        # generate mock datasets in temp-directory
        metadata_file_path = os.path.join(TempDirTestCase.TEMP_PATH, "test1.csv")
        metadata_df = pd.DataFrame(
            {"id": [0, 1, 2, 3, 4, 5], "start": [0] * 6, "end": [10] * 6}
        )
        metadata_df.to_csv(metadata_file_path, index=False)
        metadata_file_path_2 = os.path.join(TempDirTestCase.TEMP_PATH, "test2.csv")
        metadata_df_2 = pd.DataFrame({"end": [10] * 6})
        metadata_df_2.to_csv(metadata_file_path_2, index=False)
        # add data
        dataset1 = Dataset(
            dataset_name="test1", file_path="/test/path/1", filetype="cooler", user_id=1
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=1,
            file_path=intervals_file_path,
            windowsize=200000,
        )
        metadata1 = BedFileMetadata(
            file_path=metadata_file_path,
            metadata_fields='["id", "start"]',
            dataset_id=1,
        )
        metadata2 = BedFileMetadata(
            file_path=metadata_file_path_2, metadata_fields='["end"]', dataset_id=1
        )
        db.session.add_all([dataset1, intervals1, metadata1, metadata2])
        db.session.commit()
        # make apicall
        response = self.client.get(
            "/api/intervals/1/metadata",
            headers=token_headers2,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), metadata_df.to_dict(orient="list"))

    def test_entries_with_no_fields_specified_are_not_returned(self):
        """Tests whether associated metadata fiels with no field names
        specified are not returned"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers2 = self.get_token_header(token)
        # generate mock intervals in temp-directory
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
        # generate mock datasets in temp-directory
        metadata_file_path = os.path.join(TempDirTestCase.TEMP_PATH, "test1.csv")
        metadata_df = pd.DataFrame(
            {"id": [0, 1, 2, 3, 4, 5], "start": [0] * 6, "end": [10] * 6}
        )
        metadata_df.to_csv(metadata_file_path, index=False)
        metadata_file_path_2 = os.path.join(TempDirTestCase.TEMP_PATH, "test2.csv")
        metadata_df_2 = pd.DataFrame({"end": [10] * 6})
        metadata_df_2.to_csv(metadata_file_path_2, index=False)
        # add data
        dataset1 = Dataset(
            dataset_name="test1", file_path="/test/path/1", filetype="cooler", user_id=1
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=1,
            file_path=intervals_file_path,
            windowsize=200000,
        )
        metadata1 = BedFileMetadata(
            file_path=metadata_file_path,
            metadata_fields='["id", "start"]',
            dataset_id=1,
        )
        metadata2 = BedFileMetadata(file_path=metadata_file_path_2, dataset_id=1)
        db.session.add_all([dataset1, intervals1, metadata1, metadata2])
        db.session.commit()
        # make apicall
        response = self.client.get(
            "/api/intervals/1/metadata",
            headers=token_headers2,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            metadata_df.drop(labels="end", axis="columns").to_dict(orient="list"),
        )

    def test_metadata_entries_with_overlapping_fieldname_are_returned_correctly(self):
        """Tests whether multiple associated metadata entries to
        interval file with overlapping fieldnames returned the newest field (by larger id value)"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers2 = self.get_token_header(token)
        # generate mock intervals in temp-directory
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
        # generate mock datasets in temp-directory
        metadata_file_path = os.path.join(TempDirTestCase.TEMP_PATH, "test1.csv")
        metadata_df = pd.DataFrame(
            {"id": [0, 1, 2, 3, 4, 5], "start": [0] * 6, "end": [10] * 6}
        )
        metadata_df.to_csv(metadata_file_path, index=False)
        metadata_file_path_2 = os.path.join(TempDirTestCase.TEMP_PATH, "test2.csv")
        metadata_df_2 = pd.DataFrame({"end": [12] * 6})
        metadata_df_2.to_csv(metadata_file_path_2, index=False)
        # add data
        dataset1 = Dataset(
            dataset_name="test1", file_path="/test/path/1", filetype="cooler", user_id=1
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=1,
            file_path=intervals_file_path,
            windowsize=200000,
        )
        metadata1 = BedFileMetadata(
            id=1,
            file_path=metadata_file_path_2,
            metadata_fields='["end"]',
            dataset_id=1,
        )
        metadata2 = BedFileMetadata(
            id=2,
            file_path=metadata_file_path,
            metadata_fields='["id", "start", "end"]',
            dataset_id=1,
        )
        db.session.add_all([dataset1, intervals1, metadata1, metadata2])
        db.session.commit()
        # make apicall
        response = self.client.get(
            "/api/intervals/1/metadata",
            headers=token_headers2,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), metadata_df.to_dict(orient="list"))

    def test_metadata_entry_with_rows_differing_from_intervals_returned_correctly(self):
        """Context: A metadata file is associated with the bedfile and has an equal number
        of rows. However, the interval file that is associated with the bedfile does not necessarliy
        have the same number of rows because some intervals may be filtered out because the overlap
        chromosomal boundaries. This test checks whether such a case is handled correctly."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers2 = self.get_token_header(token)
        # generate mock intervals in temp-directory
        intervals_file_path = os.path.join(TempDirTestCase.TEMP_PATH, "test.bedpe")
        intervals_df = pd.DataFrame(
            {
                "chrom": ["chr1"] * 6,
                "start": [0] * 6,
                "end": [10] * 6,
                "bed_row_id": [0, 2, 4, 6, 8, 10],
            }
        )
        intervals_df.to_csv(intervals_file_path, index=False, header=None, sep="\t")
        # generate mock metadata in temp-directory
        metadata_file_path = os.path.join(TempDirTestCase.TEMP_PATH, "test.csv")
        metadata_df = pd.DataFrame(
            {"id": range(11), "start": range(11), "end": range(1, 12)}
        )
        metadata_df.to_csv(metadata_file_path, index=False)
        # add data
        dataset1 = Dataset(
            dataset_name="test1", file_path="/test/path/1", filetype="cooler", user_id=1
        )
        intervals1 = Intervals(
            name="testRegion1",
            dataset_id=1,
            file_path=intervals_file_path,
            windowsize=200000,
        )
        metadata1 = BedFileMetadata(
            file_path=metadata_file_path,
            metadata_fields='["id", "start", "end"]',
            dataset_id=1,
        )
        db.session.add_all([dataset1, intervals1, metadata1])
        db.session.commit()
        # make apicall
        response = self.client.get(
            "/api/intervals/1/metadata",
            headers=token_headers2,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            metadata_df.iloc[intervals_df["bed_row_id"], :].to_dict(orient="list"),
        )


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
