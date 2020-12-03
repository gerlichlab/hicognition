from test_helpers import LoginTestCase

# add path to import app
import sys

sys.path.append("./")
from app import db
from app.models import Dataset, Task


class TestSetProcessingState(LoginTestCase):
    """Tests whether set_processing_state
    does its job."""

    def add_test_datasets(self, state):
        """adds test datasets to db"""
        dataset1 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            higlass_uuid="asdf1234",
            filetype="cooler",
            processing_state=state,
            user_id=1,
        )
        db.session.add(dataset1)
        db.session.commit()

    def test_processing_when_task(self):
        """Tests whether processing status is set correctly 
        when there is a running task for dataset."""
        # add new user
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add new datasets
        self.add_test_datasets("uploaded")
        # add Task
        new_task = Task(id="asdf", name="test", dataset_id=1)
        db.session.add(new_task)
        db.session.commit()
        # set processing state
        dataset = Dataset.query.get(1)
        dataset.set_processing_state(db)
        # get datasets
        self.assertEqual(dataset.processing_state, "processing")

    def test_finished_when_no_task(self):
        # add new user
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add new datasets
        self.add_test_datasets("uploaded")
        # set processing state
        dataset = Dataset.query.get(1)
        dataset.set_processing_state(db)
        self.assertEqual(dataset.processing_state, "finished")

    def test_uploaded_no_update_wo_task(self):
        # add new user
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add new datasets
        self.add_test_datasets("uploading")
        # set processing state
        dataset = Dataset.query.get(1)
        dataset.set_processing_state(db)
        self.assertEqual(dataset.processing_state, "uploading")

    def test_uploaded_no_update_w_task(self):
        # add new user
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add new datasets
        self.add_test_datasets("uploading")
        # add Task
        new_task = Task(id="asdf", name="test", dataset_id=1)
        db.session.add(new_task)
        db.session.commit()
        # set processing state
        dataset = Dataset.query.get(1)
        dataset.set_processing_state(db)
        self.assertEqual(dataset.processing_state, "uploading")
