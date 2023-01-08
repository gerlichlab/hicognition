"""Module with the tests for the pyLOLA calculation realted tasks."""
import os
import unittest
from unittest.mock import patch
import pandas as pd
import numpy as np
from tests.test_utils.test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
# import sys
# sys.path.append("./")
from app import db
from app.models import (
    Dataset,
    Intervals,
    Collection,
    AssociationIntervalData,
    Assembly,
    Task,
)
from app.pipeline_steps import enrichment_pipeline_step
from app.pipeline_worker_functions import (
    _do_enrichment_calculations_fixed_size,
    _do_enrichment_calculations_variable_size,
)
from app.tasks import pipeline_lola


class TestPipelineLola(LoginTestCase):
    """Tests for pipeline lola"""

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
        # add region
        self.bedfile = self.create_dataset(id=1, dataset_name="test", filetype="bedfile", user_id=1, assembly=1)
        # add intervals
        self.intervals1 = Intervals(
            id=1, name="testRegion1", dataset_id=1, windowsize=200000
        )
        # add collections
        self.collection = Collection(id=1)
        # add tasks
        self.finished_task1 = Task(
            id="test1", collection_id=1, intervals_id=1, complete=True
        )
        self.unfinished_task1 = Task(
            id="test1", collection_id=1, intervals_id=1, complete=False
        )

    @patch("app.pipeline_steps.set_task_progress")
    @patch("app.pipeline_steps.enrichment_pipeline_step")
    def test_dataset_state_not_changed_if_not_last(
        self, mock_enrichment, mock_set_progress
    ):
        """tests whether dataset state is left unchanged if it is not the last task for
        this dataset/intervals combination."""
        # set up database
        self.bedfile.processing_collections = [self.collection]
        db.session.add_all(
            [self.bedfile, self.collection, self.intervals1, self.unfinished_task1]
        )
        # call pipeline
        pipeline_lola(1, 1, 10000)
        # check whether processing has finished
        self.assertEqual(self.bedfile.processing_collections, [self.collection])

    @patch("app.pipeline_steps.set_task_progress")
    @patch("app.pipeline_steps.enrichment_pipeline_step")
    def test_dataset_set_finished_if_last(self, mock_enrichment, mock_set_progress):
        """tests whether dataset is set finished correctly if it is the last task for
        this dataset/intervals combination."""
        # set up database
        self.bedfile.processing_collections = [self.collection]
        db.session.add_all(
            [self.bedfile, self.collection, self.intervals1, self.finished_task1]
        )
        # call pipeline
        pipeline_lola(1, 1, 10000)
        # check whether processing has finished
        self.assertEqual(self.bedfile.processing_collections, [])

    @patch("app.pipeline_steps.current_app.logger.error")
    @patch("app.pipeline_steps.set_task_progress")
    @patch("app.pipeline_steps.enrichment_pipeline_step")
    def test_dataset_set_failed_if_failed(
        self, mock_enrichment, mock_set_progress, mock_log
    ):
        """tests whether dataset is set as faild if problem arises."""
        # set up exception raising
        mock_enrichment.side_effect = ValueError("Test")
        # set up database
        self.bedfile.processing_collections = [self.collection]
        db.session.add_all(
            [self.bedfile, self.collection, self.intervals1, self.finished_task1]
        )
        # call pipeline
        pipeline_lola(1, 1, 10000)
        # check whether processing has finished
        self.assertEqual(self.bedfile.failed_collections, [self.collection])
        self.assertEqual(self.bedfile.processing_collections, [])
        assert mock_log.called


class EnrichmentSetupClass(LoginTestCase, TempDirTestCase):
    """Class that contains shared data setup methods for the testclass
    for enrichment"""

    def _create_empty_file_in_tempdir(self, file_name):
        file_path = os.path.join(self.TEMP_PATH, file_name)
        open(file_path, "w").close()
        return file_path

    def _populate_with_data(self):
        source_data = pd.read_csv(
            "tests/testfiles/test3_realData_large.bed", sep="\t", header=None
        )
        self.target_1 = source_data.iloc[8000:12000, :]
        self.target_2 = source_data.iloc[2000:8000, :]
        self.positions = source_data.iloc[4000:10000, :]
        # write to file
        target_1_file = os.path.join(self.TEMP_PATH, "target_1.bed")
        self.target_1.to_csv(target_1_file, header=None, sep="\t", index=False)
        target_2_file = os.path.join(self.TEMP_PATH, "target_2.bed")
        self.target_2.to_csv(target_2_file, header=None, sep="\t", index=False)
        pos_file = os.path.join(self.TEMP_PATH, "pos.bed")
        self.positions.to_csv(pos_file, header=None, sep="\t", index=False)
        # create datasets
        self.query_dataset = self.create_dataset(
            id=1, dataset_name="test", user_id=1, file_path=pos_file, filetype="bedfile", assembly=1
        )
        self.target_dataset_1 = self.create_dataset(
            id=2, dataset_name="test", user_id=1, file_path=target_1_file, filetype="bedfile", assembly=1
        )
        self.target_dataset_2 = self.create_dataset(
            id=3, dataset_name="test", user_id=1, file_path=target_2_file, filetype="bedfile", assembly=1
        )
        # create intervals
        self.query_interval = Intervals(id=1, windowsize=100000, dataset_id=1)
        # create collections
        self.collection_1 = Collection(
            id=1, datasets=[self.target_dataset_1, self.target_dataset_2]
        )
        # create AssociationIntervalData
        test_file = self._create_empty_file_in_tempdir("asdf.npy")
        self.assoc_data_1 = AssociationIntervalData(
            file_path=test_file, binsize=50000, collection_id=1, intervals_id=1
        )
        # add tad boundaries
        self.tad_boundaries = self.create_dataset(
            id=4, dataset_name="test",
            file_path="tests/testfiles/tad_boundaries.bed",
            filetype="bedfile",
            assembly=1,
            user_id=1
        )
        self.tad_boundaries_interval = Intervals(id=2, windowsize=200000, dataset_id=4)
        # add ctcf peaks
        self.ctcf_peaks = self.create_dataset(
            id=5, dataset_name="test",
            file_path="tests/testfiles/CTCF_peaks.bed",
            filetype="bedfile",
            assembly=1,
            user_id=1
        )
        self.collection_2 = Collection(id=2, datasets=[self.tad_boundaries])
        self.collection_3 = Collection(id=3, datasets=[self.ctcf_peaks])
        # add variable intervals
        self.tads = self.create_dataset(
            id=6, dataset_name="test",
            file_path="tests/testfiles/G2_tads_w_size.bed",
            filetype="bedfile",
            assembly=1,
            sizeType="Interval",
            user_id=1
        )
        self.tad_interval = Intervals(id=3, dataset_id=6)

    def _create_groupings(self):
        self.datasets = [
            self.query_dataset,
            self.tad_boundaries,
            self.target_dataset_1,
            self.target_dataset_2,
            self.tads,
            self.ctcf_peaks,
        ]
        self.intervals = [
            self.query_interval,
            self.tad_boundaries_interval,
            self.tad_interval,
        ]
        self.collections = [self.collection_1, self.collection_2, self.collection_3]

    def setUp(self):
        """Add test dataset"""
        # call setUp of LoginTestCase to initialize app
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
        self._populate_with_data()
        self._create_groupings()


class TestEnrichmentPipelineStep(EnrichmentSetupClass):
    """Tests enrichment pipeline step"""

    @patch("app.pipeline_steps.worker_funcs._do_enrichment_calculations_fixed_size")
    @patch("app.pipeline_steps.worker_funcs._do_enrichment_calculations_variable_size")
    def test_correct_worker_function_called_fixed_intervals(
        self, mock_variable_enrichment, mock_fixed_enrichment
    ):
        """Tests whether correct enrichment function is called for intervals with fixed size."""
        # add everything needed to database
        db.session.add_all(self.datasets)
        db.session.add_all(self.intervals)
        db.session.add_all(self.collections)
        db.session.commit()
        # run enrichment analysis
        enrichment_pipeline_step(self.collection_1.id, self.query_interval.id, 50000)
        # check functions
        mock_variable_enrichment.assert_not_called()
        mock_fixed_enrichment.assert_called()

    @patch("app.pipeline_steps.worker_funcs._do_enrichment_calculations_fixed_size")
    @patch("app.pipeline_steps.worker_funcs._do_enrichment_calculations_variable_size")
    def test_correct_worker_function_called_variable_intervals(
        self, mock_variable_enrichment, mock_fixed_enrichment
    ):
        """Tests whether correct enrichment function is called for intervals with variable size."""
        # add everything needed to database
        db.session.add_all(self.datasets)
        db.session.add_all(self.intervals)
        db.session.add_all(self.collections)
        db.session.commit()
        # run enrichment analysis
        enrichment_pipeline_step(self.collection_1.id, self.tad_interval.id, 50000)
        # check functions
        mock_variable_enrichment.assert_called()
        mock_fixed_enrichment.assert_not_called()

    def test_result_added_correctly_to_db(self):
        """tests whether perform enrichment analysis adds result correctly to db."""
        # add everything needed to database
        db.session.add_all(self.datasets)
        db.session.add_all(self.intervals)
        db.session.add_all(self.collections)
        db.session.commit()
        # run enrichment analysis
        enrichment_pipeline_step(self.collection_1.id, self.query_interval.id, 50000)
        # check database state
        self.assertEqual(len(AssociationIntervalData.query.all()), 1)
        result = AssociationIntervalData.query.first()
        self.assertEqual(result.intervals_id, 1)
        self.assertEqual(result.binsize, 50000)
        self.assertEqual(result.collection_id, 1)

    def test_old_association_data_removed_when_retriggered(self):
        """tests whether perform enrichment analysis adds result correctly to db."""
        # add everything needed to database
        db.session.add_all(self.datasets)
        db.session.add_all(self.intervals)
        db.session.add_all(self.collections)
        db.session.add(self.assoc_data_1)
        db.session.commit()
        # run enrichment analysis
        enrichment_pipeline_step(self.collection_1.id, self.query_interval.id, 50000)
        # check database state
        self.assertEqual(len(AssociationIntervalData.query.all()), 1)
        result = AssociationIntervalData.query.first()
        self.assertEqual(result.intervals_id, 1)
        self.assertEqual(result.binsize, 50000)
        self.assertEqual(result.collection_id, 1)


class TestEnrichmentWorkerFunctionFixedSize(EnrichmentSetupClass):
    """tests for enrichment worker function for regions
    with fixed size"""

    def test_result_correct(self):
        """tests whether result is correct for a small example"""
        # add everything needed to database
        db.session.add_all(self.datasets)
        db.session.add_all(self.intervals)
        db.session.add_all(self.collections)
        db.session.commit()
        # run enrichment analysis
        result = _do_enrichment_calculations_fixed_size(
            self.collection_1.id,
            self.query_interval.windowsize,
            50000,
            self.query_interval.source_dataset.file_path,
        )
        expected = np.array(
            [
                [7.02834217, 8.09706518, 25.87762319, 8.07835162],
                [15.63264795, 18.78167934, 113.33089378, 18.7916413],
            ]
        )
        self.assertTrue(np.all(np.isclose(result, expected)))

    def test_query_in_targets_does_not_crash(self):
        """Tests whether query with duplicates is handled correctly."""
        db.session.add_all(self.datasets)
        db.session.add_all(self.intervals)
        db.session.add_all(self.collections)
        db.session.commit()
        # run enrichment analysis
        _do_enrichment_calculations_fixed_size(
            self.collection_2.id,
            self.tad_boundaries_interval.windowsize,
            50000,
            self.tad_boundaries_interval.source_dataset.file_path,
        )


class TestEnrichmentWorkerFunctionVariableSize(EnrichmentSetupClass):
    """tests for enrichment worker function for regions
    with variable size"""

    def test_variable_sized_regions_run_through(self):
        """tests whether enrichment for variable sized regions runs correctly."""
        db.session.add_all(self.datasets)
        db.session.add_all(self.intervals)
        db.session.add_all(self.collections)
        db.session.commit()
        # run enrichment analysis
        _do_enrichment_calculations_variable_size(
            self.collection_2.id, 10, self.tad_interval.source_dataset.file_path
        )


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
