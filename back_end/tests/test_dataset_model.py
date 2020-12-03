from test_helpers import LoginTestCase
# add path to import app
import sys
sys.path.append("./")
from app import db
from app.models import Dataset, Task

class TestGetDatasets(LoginTestCase):
    """Tests for /api/datasets route to list
    datasets."""

    def add_test_datasets(self):
        """adds test datasets to db"""
        dataset1 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            higlass_uuid="asdf1234",
            filetype="cooler",
            processing_state="finished",
            user_id=1
        )
        dataset2 = Dataset(
            dataset_name="test2",
            file_path="/test/path/2",
            higlass_uuid="fdsa4321",
            filetype="cooler",
            processing_state="finished",
            user_id=1
        )
        dataset3 = Dataset(
            dataset_name="test3",
            file_path="/test/path/3",
            higlass_uuid="fdsa8765",
            filetype="bedfile",
            processing_state="finished",
            user_id=1
        )
        db.session.add(dataset1)
        db.session.add(dataset2)
        db.session.add(dataset3)
        db.session.commit()

    def test_completed_flag_updates(self):
        """Tests whether the completed flag of datasets updates
        when an unfinished task is present"""
        # add new user
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add new datasets
        self.add_test_datasets()
        # add Task
        new_task = Task(id="asdf", name="test", dataset_id=1)
        db.session.add(new_task)
        db.session.commit()
         # get datasets
        response = self.client.get(
            "/api/datasets/", headers=token_headers, content_type="application/json",
        )
        # check response
        self.assertEqual(response.status_code, 200)
        expected = [
            {
                "dataset_name": "test1",
                "file_path": "/test/path/1",
                "filetype": "cooler",
                "higlass_uuid": "asdf1234",
                "id": 1,
                "user_id": 1,
                "completed": 0
            },
            {
                "dataset_name": "test2",
                "file_path": "/test/path/2",
                "filetype": "cooler",
                "higlass_uuid": "fdsa4321",
                "id": 2,
                "user_id": 1,
                "processing_state": "finished"
            },
            {
                "dataset_name": "test3",
                "file_path": "/test/path/3",
                "filetype": "bedfile",
                "higlass_uuid": "fdsa8765",
                "id": 3,
                "user_id": 1,
                "processing_state": "finished"
            },
        ]
        self.assertEqual(response.json, expected)