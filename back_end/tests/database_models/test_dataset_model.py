"""Tests whether preprocessing states for datasets are set correctly."""
from unittest.mock import patch
from hicognition.test_helpers import LoginTestCase

# add path to import app
# import sys
# sys.path.append("./")
from app import db
from app.models import Assembly, Dataset, Task


class TestSetProcessingState(LoginTestCase):
    """Tests whether set_processing_state
    does its job."""

    def add_test_datasets(self, state):
        """adds test datasets to db"""       
        self.hg19 = Assembly(
            id=1,
            name="hg19",
            chrom_sizes=self.app.config["CHROM_SIZES"],
            chrom_arms=self.app.config["CHROM_ARMS"],
        )
        db.session.add(self.hg19)
        dataset1 = self.create_dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            filetype="cooler",
            processing_state=state,
            user_id=1,
            assembly=1
        )
        db.session.add(dataset1)
        db.session.commit()

    @patch("app.models.any_tasks_failed")
    @patch("app.models.all_tasks_finished")
    def test_processing_when_task(self, mock_finished, mock_failed):
        """Tests whether processing status is set correctly
        when there is a running task for dataset."""
        # set return value of mock_finished and mock_failed
        mock_finished.return_value = False
        mock_failed.return_value = False
        # add new datasets
        self.add_test_datasets("processing")
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
        """Tests whether processing status is set correctly
        when there is no task for the dataset."""
        # add new datasets
        self.add_test_datasets("processing")
        # set processing state
        dataset = Dataset.query.get(1)
        dataset.set_processing_state(db)
        self.assertEqual(dataset.processing_state, "finished")

    def test_uploaded_no_update_wo_task(self):
        """Tests whether processing status is set correctly
        when a dataset wo tasks has an uploading status."""
        # add new datasets
        self.add_test_datasets("uploading")
        # set processing state
        dataset = Dataset.query.get(1)
        dataset.set_processing_state(db)
        self.assertEqual(dataset.processing_state, "uploading")

    def test_uploaded_no_update_w_task(self):
        """Tests whether processing status is set correctly
        when a dataset with tasks has an uploading status."""
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
