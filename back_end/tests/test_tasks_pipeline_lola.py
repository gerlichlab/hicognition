import sys
import os
import unittest
import pandas as pd
import numpy as np
from test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
sys.path.append("./")
from app import db
from app.models import Dataset, Intervals, Collection, AssociationIntervalData
from app.pipeline_steps import perform_enrichment_analysis


class TestPerformEnrichmentAnalysis(LoginTestCase, TempDirTestCase):
    """Tests bed_preprocess_pipeline_step"""

    def _create_empty_file_in_tempdir(self, file_name):
        file_path = os.path.join(self.TEMP_PATH, file_name)
        open(file_path, "w").close()
        return file_path

    def setUp(self):
        """Add test dataset"""
        # call setUp of LoginTestCase to initialize app
        super().setUp()
        # load bedfile that is used to derive other bedfiles
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
        self.query_dataset = Dataset(id=1, file_path=pos_file, filetype="bedfile")
        self.target_dataset_1 = Dataset(
            id=2, file_path=target_1_file, filetype="bedfile"
        )
        self.target_dataset_2 = Dataset(
            id=3, file_path=target_2_file, filetype="bedfile"
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
        # create groupings
        self.datasets = [
            self.query_dataset,
            self.target_dataset_1,
            self.target_dataset_2,
        ]
        self.intervals = [self.query_interval]
        self.collections = [self.collection_1]

    def test_result_added_correctly_to_db(self):
        """tests whether perform enrichment analysis adds result correctly to db."""
        # add everything needed to database
        db.session.add_all(self.datasets)
        db.session.add_all(self.intervals)
        db.session.add_all(self.collections)
        db.session.commit()
        # run enrichment analysis
        perform_enrichment_analysis(self.collection_1.id, self.query_interval.id, 50000)
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
        perform_enrichment_analysis(self.collection_1.id, self.query_interval.id, 50000)
        # check database state
        self.assertEqual(len(AssociationIntervalData.query.all()), 1)
        result = AssociationIntervalData.query.first()
        self.assertEqual(result.intervals_id, 1)
        self.assertEqual(result.binsize, 50000)
        self.assertEqual(result.collection_id, 1)

    def test_result_correct(self):
        """tests whether result added to db is correct"""
        # add everything needed to database
        db.session.add_all(self.datasets)
        db.session.add_all(self.intervals)
        db.session.add_all(self.collections)
        db.session.commit()
        # run enrichment analysis
        perform_enrichment_analysis(self.collection_1.id, self.query_interval.id, 50000)
        # load result
        result = AssociationIntervalData.query.first()
        data_result = np.load(result.file_path)
        expected = np.array(
            [
                [7.02834217, 8.09706518, 25.87762319, 8.07835162],
                [15.63264795, 18.78167934, 113.33089378, 18.7916413],
            ]
        )
        self.assertTrue(np.all(np.isclose(data_result, expected)))


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
