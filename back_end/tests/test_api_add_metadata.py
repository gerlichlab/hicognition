import sys
import os
import json
import io
import unittest
import pandas as pd
from pandas.testing import assert_frame_equal
from test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
sys.path.append("./")
from app import db
from app.models import Dataset, BedFileMetadata


class TestAddMetadata(LoginTestCase, TempDirTestCase):
    """
    Tests for addition of metadata to existing bedfile.
    """

    def test_access_denied_without_token(self):
        """Test whether post request results in 401 error
        if no token is provided."""
        # dispatch post request
        response = self.client.post(
            "/api/bedFileMetadata/",
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 401)

    def test_access_denied_not_owned_dataset(self):
        """Tests whether access is denied for posting to
        not owned dataset."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token2 = self.add_and_authenticate(
            "test2", "fdsa"
        )  # second user that is not used
        # add dataset
        dataset = Dataset(id=1, user_id=2)
        db.session.add(dataset)
        db.session.commit()
        # create token_header
        token_headers = self.get_token_header(token)
        # add content-type
        token_headers["Content-Type"] = "multipart/form-data"
        # construct form data
        data = {
            "dataset_id": "1",
            "file": (io.BytesIO(b"abcdef"), "test.csv"),
            "separator": ",",
        }
        # dispatch post request
        response = self.client.post(
            "/api/bedFileMetadata/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 403)

    def test_invalid_form_no_dataset_id(self):
        """Tests whether for with no dataset id causes
        invalid error."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # add dataset
        dataset = Dataset(id=1, user_id=1)
        db.session.add(dataset)
        db.session.commit()
        # create token_header
        token_headers = self.get_token_header(token)
        # add content-type
        token_headers["Content-Type"] = "multipart/form-data"
        # construct form data
        data = {"file": (io.BytesIO(b"abcdef"), "test.csv"), "separator": ","}
        # dispatch post request
        response = self.client.post(
            "/api/bedFileMetadata/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    def test_invalid_form_no_separator(self):
        """Tests whether no separator in form causes
        invalid error."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # add dataset
        dataset = Dataset(id=1, user_id=1)
        db.session.add(dataset)
        db.session.commit()
        # create token_header
        token_headers = self.get_token_header(token)
        # add content-type
        token_headers["Content-Type"] = "multipart/form-data"
        # construct form data
        data = {"dataset_id": 1, "file": (io.BytesIO(b"abcdef"), "test.csv")}
        # dispatch post request
        response = self.client.post(
            "/api/bedFileMetadata/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    def test_invalid_form_no_textfile(self):
        """Tests whether wrong filetype causes
        invalid error."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # add dataset
        dataset = Dataset(id=1, user_id=1)
        db.session.add(dataset)
        db.session.commit()
        # create token_header
        token_headers = self.get_token_header(token)
        # add content-type
        token_headers["Content-Type"] = "multipart/form-data"
        # construct form data
        data = {
            "dataset_id": 1,
            "file": (io.BytesIO(b"abcdef"), "test.cool"),
            "separator": ",",
        }
        # dispatch post request
        response = self.client.post(
            "/api/bedFileMetadata/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    def test_dataset_does_not_exist(self):
        """Tests whether dataset id that does not exist causes 404 error."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # add dataset
        dataset = Dataset(id=1, user_id=1)
        db.session.add(dataset)
        db.session.commit()
        # create token_header
        token_headers = self.get_token_header(token)
        # add content-type
        token_headers["Content-Type"] = "multipart/form-data"
        # construct form data
        data = {
            "dataset_id": 500,
            "file": (io.BytesIO(b"abcdef"), "test.csv"),
            "separator": ",",
        }
        # dispatch post request
        response = self.client.post(
            "/api/bedFileMetadata/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 404)

    def test_length_missmatch_dataset_metadata(self):
        """Tests whether length missmatch between
        dataset and metadata is detected."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create dataset file
        test_filepath = os.path.join(TempDirTestCase.TEMP_PATH, "test.bed")
        test_data = pd.DataFrame(
            {"id": [0, 1, 2, 3, 4, 5], "start": [0] * 6, "end": [10] * 6}
        )
        test_data.to_csv(test_filepath, sep="\t")
        # create paylod_file
        payload_filepath = os.path.join(TempDirTestCase.TEMP_PATH, "payload.bed")
        payload_data = pd.DataFrame(
            {"id": [0, 1, 2, 3], "start": [0] * 4, "end": [10] * 4}
        )
        payload_data.to_csv(payload_filepath, sep="\t")
        # add dataset
        dataset = Dataset(id=1, user_id=1, file_path=test_filepath)
        db.session.add(dataset)
        db.session.commit()
        # create token_header
        token_headers = self.get_token_header(token)
        # add content-type
        token_headers["Content-Type"] = "multipart/form-data"
        # construct form data
        data = {
            "dataset_id": 1,
            "file": (open(payload_filepath, "rb"), "test.csv"),
            "separator": "\t",
        }
        # dispatch post request
        response = self.client.post(
            "/api/bedFileMetadata/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(), {"ValidationError": "Dataset length missmatch!"}
        )

    def test_valid_metadata_added_correctly(self):
        """Tests whether valid metadata dataset is added correctly."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create dataset file
        test_filepath = os.path.join(TempDirTestCase.TEMP_PATH, "test.bed")
        test_data = pd.DataFrame(
            {"id": [0, 1, 2, 3, 4, 5], "start": [0] * 6, "end": [10] * 6}
        )
        test_data.to_csv(test_filepath, sep="\t", index=False)
        # create paylod_file
        payload_filepath = os.path.join(TempDirTestCase.TEMP_PATH, "payload.bed")
        payload_data = pd.DataFrame(
            {"size": [0, 1, 2, 3, 4, 5], "start": [0] * 6, "end": [10] * 6}
        )
        payload_data.to_csv(payload_filepath, sep="\t", index=False)
        # add dataset
        dataset = Dataset(id=1, user_id=1, file_path=test_filepath)
        db.session.add(dataset)
        db.session.commit()
        # create token_header
        token_headers = self.get_token_header(token)
        # add content-type
        token_headers["Content-Type"] = "multipart/form-data"
        # construct form data
        data = {
            "dataset_id": 1,
            "file": (open(payload_filepath, "rb"), "test.csv"),
            "separator": "\t",
        }
        # dispatch post request
        response = self.client.post(
            "/api/bedFileMetadata/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        # check whether metadata database entry was created and links to correct dataset
        self.assertEqual(1, len(BedFileMetadata.query.all()))
        metadata = BedFileMetadata.query.first()
        self.assertEqual(metadata.dataset_id, 1)
        # check whether dataframe is ok
        test_dataframe = pd.read_csv(metadata.file_path)
        assert_frame_equal(test_dataframe, payload_data)

    def test_valid_metadata_with_string_columns_added_correctly(self):
        """Tests whether valid metadata dataset is added correctly
        even if it contains string columns"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create dataset file
        test_filepath = os.path.join(TempDirTestCase.TEMP_PATH, "test.bed")
        test_data = pd.DataFrame(
            {"id": [0, 1, 2, 3, 4, 5], "start": [0] * 6, "end": [10] * 6}
        )
        test_data.to_csv(test_filepath, sep="\t", index=False)
        # create paylod_file
        payload_filepath = os.path.join(TempDirTestCase.TEMP_PATH, "payload.bed")
        payload_data = pd.DataFrame(
            {
                "size": [0, 1, 2, 3, 4, 5],
                "start": [0] * 6,
                "end": [10] * 6,
                "string_column": ["asdf"] * 6,
            }
        )
        payload_data.to_csv(payload_filepath, sep="\t", index=False)
        # add dataset
        dataset = Dataset(id=1, user_id=1, file_path=test_filepath)
        db.session.add(dataset)
        db.session.commit()
        # create token_header
        token_headers = self.get_token_header(token)
        # add content-type
        token_headers["Content-Type"] = "multipart/form-data"
        # construct form data
        data = {
            "dataset_id": 1,
            "file": (open(payload_filepath, "rb"), "test.csv"),
            "separator": "\t",
        }
        # dispatch post request
        response = self.client.post(
            "/api/bedFileMetadata/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        # check whetehr numeric fields are returned
        self.assertEqual(
            response.get_json(),
            {
                "message": "success! Preprocessing triggered.",
                "field_names": list(
                    sorted(payload_data.drop("string_column", axis="columns"))
                ),
            },
        )
        # check whether metadata database entry was created and links to correct dataset
        self.assertEqual(1, len(BedFileMetadata.query.all()))
        metadata = BedFileMetadata.query.first()
        self.assertEqual(metadata.dataset_id, 1)
        # check whether dataframe is ok
        test_dataframe = pd.read_csv(metadata.file_path)
        assert_frame_equal(
            test_dataframe, payload_data.drop("string_column", axis="columns")
        )

class TestAddMetadataFields(LoginTestCase, TempDirTestCase):
    """Tests whether setting relevant metadata fields with key-value-pairs
    where key is a valid metadata columns and the value is the wanted display name
     works."""

    def test_access_denied_without_token(self):
        """Test whether post request results in 401 error
        if no token is provided."""
        # dispatch post request
        response = self.client.post(
            "/api/bedFileMetadata/1/setFields",
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 401)

    def test_access_denied_not_owned_metadata(self):
        """Tests whether access is denied for posting to
        metadata associated with not owned dataset"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token2 = self.add_and_authenticate(
            "test2", "fdsa"
        )  # second user that is not used
        # add dataset and metadata
        dataset = Dataset(id=1, user_id=2)
        metadata = BedFileMetadata(id=1, dataset_id=1)
        db.session.add(dataset)
        db.session.add(metadata)
        db.session.commit()
        # create token_header
        token_headers = self.get_token_header(token)
        # add content-type
        token_headers["Content-Type"] = "multipart/form-data"
        # construct form data
        data = {
            "fields": json.dumps({"asdf": "fdsa"}),
        }
        # dispatch post request
        response = self.client.post(
            "/api/bedFileMetadata/1/setFields",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 403)

    def test_non_existing_metadata(self):
        """Tests whether 404 error is returned for non-exisitng
        metadata."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # add dataset and metadata
        dataset = Dataset(id=1, user_id=1)
        metadata = BedFileMetadata(id=1, dataset_id=1)
        db.session.add(dataset)
        db.session.add(metadata)
        db.session.commit()
        # create token_header
        token_headers = self.get_token_header(token)
        # add content-type
        token_headers["Content-Type"] = "multipart/form-data"
        # construct form data
        data = {
            "fields": json.dumps({"asdf": "fdsa"}),
        }
        # dispatch post request
        response = self.client.post(
            "/api/bedFileMetadata/500/setFields",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 404)

    def test_non_existing_field(self):
        """Tests whether invalid error is raised if 
        field specified does not exist in the metadata."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # generate metadata file
        metadata_filepath = os.path.join(TempDirTestCase.TEMP_PATH, "metadata.txt")
        metadata_data = pd.DataFrame(
            {
                "size": [0, 1, 2, 3, 4, 5],
                "start": [0] * 6,
                "end": [10] * 6,
            }
        )
        metadata_data.to_csv(metadata_filepath, index=False)
        # add dataset and metadata
        dataset = Dataset(id=1, user_id=1)
        metadata = BedFileMetadata(id=1, dataset_id=1, file_path=metadata_filepath)
        db.session.add(dataset)
        db.session.add(metadata)
        db.session.commit()
        # create token_header
        token_headers = self.get_token_header(token)
        # add content-type
        token_headers["Content-Type"] = "multipart/form-data"
        # construct form data
        data = {
            "fields": json.dumps({"asdf": "fdsa"}),
        }
        # dispatch post request
        response = self.client.post(
            "/api/bedFileMetadata/1/setFields",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    def test_field_map_added_correclty(self):
        """Tests whether correct field_name specification is
        added correctly."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # generate metadata file
        metadata_filepath = os.path.join(TempDirTestCase.TEMP_PATH, "metadata.txt")
        metadata_data = pd.DataFrame(
            {
                "size": [0, 1, 2, 3, 4, 5],
                "start": [0] * 6,
                "end": [10] * 6,
            }
        )
        metadata_data.to_csv(metadata_filepath, index=False)
        # add dataset and metadata
        dataset = Dataset(id=1, user_id=1)
        metadata = BedFileMetadata(id=1, dataset_id=1, file_path=metadata_filepath)
        db.session.add(dataset)
        db.session.add(metadata)
        db.session.commit()
        # create token_header
        token_headers = self.get_token_header(token)
        # add content-type
        token_headers["Content-Type"] = "multipart/form-data"
        # construct form data
        data = {
            "fields": json.dumps({"size": "Size", "start": "Start"}),
        }
        # dispatch post request
        response = self.client.post(
            "/api/bedFileMetadata/1/setFields",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        # check whether fields were added correctly
        metadata = BedFileMetadata.query.get(1)
        actual = metadata.metadata_fields
        expected = json.dumps({"size": "Size", "start": "Start"})
        self.assertEqual(actual, expected)

if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
