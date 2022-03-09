"""Tests whether preprocessing states for collections are set correctly."""
import unittest
from unittest.mock import patch
from hicognition.test_helpers import LoginTestCase
# add path to import app
# import sys
# sys.path.append("./")
from app import db
from app.models import Collection, Task


class TestSetProcessingState(LoginTestCase):
    """Tests whether set_processing_state
    does its job."""

    def add_test_collection(self, state):
        """adds test collection to db
        with specified processing state."""
        collection = Collection(processing_state=state)
        db.session.add(collection)
        db.session.commit()

    @patch("app.models.any_tasks_failed")
    @patch("app.models.all_tasks_finished")
    def test_processing_when_task(self, mock_finished, mock_failed):
        """Tests whether processing status is set correctly
        when there is a running task for collection."""
        # set return value of mock_finished and mock_failed
        mock_finished.return_value = False
        mock_failed.return_value = False
        # add new collection
        self.add_test_collection("processing")
        # add Task
        new_task = Task(id="asdf", name="test", collection_id=1)
        db.session.add(new_task)
        db.session.commit()
        # set processing state
        collection = Collection.query.get(1)
        collection.set_processing_state(db)
        # get datasets
        self.assertEqual(collection.processing_state, "processing")

    def test_finished_when_no_task(self):
        # add new datasets
        self.add_test_collection("processing")
        # set processing state
        collection = Collection.query.get(1)
        collection.set_processing_state(db)
        self.assertEqual(collection.processing_state, "finished")

    def test_uploaded_no_update_wo_task(self):
        # add new datasets
        self.add_test_collection("uploading")
        # set processing state
        collection = Collection.query.get(1)
        collection.set_processing_state(db)
        self.assertEqual(collection.processing_state, "uploading")

    def test_uploaded_no_update_w_task(self):
        # add new datasets
        self.add_test_collection("uploading")
        # add Task
        new_task = Task(id="asdf", name="test", dataset_id=1)
        db.session.add(new_task)
        db.session.commit()
        # set processing state
        collection = Collection.query.get(1)
        collection.set_processing_state(db)
        self.assertEqual(collection.processing_state, "uploading")


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
