"""Tests for db manipulation of tasks"""
import unittest
from hicognition.test_helpers import LoginTestCase
from app.pipeline_worker_functions import (
    _add_embedding_2d_to_db,
    _add_embedding_1d_to_db,
    _add_association_data_to_db,
    _add_stackup_db,
    _add_line_db,
    _add_pileup_db
)
from app.models import EmbeddingIntervalData, AssociationIntervalData, IndividualIntervalData, AverageIntervalData


class TestAddEmbedding2DToDB(LoginTestCase):
    """Tests for adding 2D-embeddings to db"""

    def setUp(self):
        super().setUp()
        self.filepaths_1 = {
            "embedding": "test/embedding_test",
            "thumbnails": "test/thumbnail",
            "cluster_ids": "test/cluster_ids",
        }
        self.filepaths_2 = {
            "embedding": "test/embedding_test2",
            "thumbnails": "test/thumbnail2",
            "cluster_ids": "test/cluster_ids2",
        }

    def test_add_new_entry_if_no_conflict(self):
        """Tests whether a new entry is added if there is
        no entry in db that satisfies the parameter constraints."""
        _add_embedding_2d_to_db(
            self.filepaths_1,
            binsize=10000,
            intervals_id=1,
            dataset_id=1,
            interaction_type="ICCF",
            cluster_number=10,
        )
        self.assertEqual(len(EmbeddingIntervalData.query.all()), 1)
        entry = EmbeddingIntervalData.query.first()
        self.assertEqual(entry.name, "embedding_test")
        self.assertEqual(entry.binsize, 10000)
        self.assertEqual(entry.intervals_id, 1)
        self.assertEqual(entry.dataset_id, 1)
        self.assertEqual(entry.file_path, self.filepaths_1["embedding"])
        self.assertEqual(entry.thumbnail_path, self.filepaths_1["thumbnails"])
        self.assertEqual(entry.cluster_id_path, self.filepaths_1["cluster_ids"])
        self.assertEqual(entry.value_type, "2d-embedding")
        self.assertEqual(entry.normalization, "ICCF")
        self.assertEqual(entry.cluster_number, "10")

    def test_entry_updated_if_conflict(self):
        """Tests whether a new entry is added if there is
        no entry in db that satisfies the parameter constraints."""
        # add first entry
        _add_embedding_2d_to_db(
            self.filepaths_1,
            binsize=10000,
            intervals_id=1,
            dataset_id=1,
            interaction_type="ICCF",
            cluster_number=10,
        )
        first_id = EmbeddingIntervalData.query.first().id
        # add second entry
        _add_embedding_2d_to_db(
            self.filepaths_2,
            binsize=10000,
            intervals_id=1,
            dataset_id=1,
            interaction_type="ICCF",
            cluster_number=10,
        )
        self.assertEqual(len(EmbeddingIntervalData.query.all()), 1)
        entry = EmbeddingIntervalData.query.first()
        self.assertEqual(first_id, entry.id)
        self.assertEqual(entry.name, "embedding_test2")
        self.assertEqual(entry.binsize, 10000)
        self.assertEqual(entry.intervals_id, 1)
        self.assertEqual(entry.dataset_id, 1)
        self.assertEqual(entry.file_path, self.filepaths_2["embedding"])
        self.assertEqual(entry.thumbnail_path, self.filepaths_2["thumbnails"])
        self.assertEqual(entry.cluster_id_path, self.filepaths_2["cluster_ids"])
        self.assertEqual(entry.value_type, "2d-embedding")
        self.assertEqual(entry.normalization, "ICCF")
        self.assertEqual(entry.cluster_number, "10")


class TestAddEmbedding1DToDB(LoginTestCase):
    """Tests for adding 1D-embeddings to db"""

    def setUp(self):
        super().setUp()
        self.filepaths_1 = {
            "embedding": "test/embedding_test",
            "features": "test/features",
            "cluster_ids": "test/cluster_ids",
            "average_values": "test/average_values",
        }
        self.filepaths_2 = {
            "embedding": "test/embedding_test2",
            "features": "test/features2",
            "cluster_ids": "test/cluster_ids2",
            "average_values": "test/average_values2",
        }

    def test_add_new_entry_if_no_conflict(self):
        """Tests whether a new entry is added if there is
        no entry in db that satisfies the parameter constraints."""
        _add_embedding_1d_to_db(
            self.filepaths_1,
            binsize=10000,
            intervals_id=1,
            collection_id=1,
            cluster_number=10,
        )
        self.assertEqual(len(EmbeddingIntervalData.query.all()), 1)
        entry = EmbeddingIntervalData.query.first()
        self.assertEqual(entry.name, "embedding_test")
        self.assertEqual(entry.binsize, 10000)
        self.assertEqual(entry.intervals_id, 1)
        self.assertEqual(entry.collection_id, 1)
        self.assertEqual(entry.file_path, self.filepaths_1["embedding"])
        self.assertEqual(entry.file_path_feature_values, self.filepaths_1["features"])
        self.assertEqual(entry.cluster_id_path, self.filepaths_1["cluster_ids"])
        self.assertEqual(entry.thumbnail_path, self.filepaths_1["average_values"])
        self.assertEqual(entry.value_type, "1d-embedding")
        self.assertEqual(entry.cluster_number, "10")

    def test_entry_updated_if_conflict(self):
        """Tests whether a new entry is added if there is
        no entry in db that satisfies the parameter constraints."""
        # add first entry
        _add_embedding_1d_to_db(
            self.filepaths_1,
            binsize=10000,
            intervals_id=1,
            collection_id=1,
            cluster_number=10,
        )
        first_id = EmbeddingIntervalData.query.first().id
        # add second entry
        _add_embedding_1d_to_db(
            self.filepaths_2,
            binsize=10000,
            intervals_id=1,
            collection_id=1,
            cluster_number=10,
        )
        self.assertEqual(len(EmbeddingIntervalData.query.all()), 1)
        entry = EmbeddingIntervalData.query.first()
        self.assertEqual(first_id, entry.id)
        self.assertEqual(entry.name, "embedding_test2")
        self.assertEqual(entry.binsize, 10000)
        self.assertEqual(entry.intervals_id, 1)
        self.assertEqual(entry.collection_id, 1)
        self.assertEqual(entry.file_path, self.filepaths_2["embedding"])
        self.assertEqual(entry.file_path_feature_values, self.filepaths_2["features"])
        self.assertEqual(entry.cluster_id_path, self.filepaths_2["cluster_ids"])
        self.assertEqual(entry.thumbnail_path, self.filepaths_2["average_values"])
        self.assertEqual(entry.value_type, "1d-embedding")
        self.assertEqual(entry.cluster_number, "10")


class TestAddAssociationDataToDB(LoginTestCase):
    """Tests for adding association data to db"""

    def test_add_new_entry_if_no_conflict(self):
        """Tests whether a new entry is added if there is
        no entry in db that satisfies the parameter constraints."""
        _add_association_data_to_db("test/path", 10000, 1, 1)
        self.assertEqual(len(AssociationIntervalData.query.all()), 1)
        entry = AssociationIntervalData.query.first()
        self.assertEqual(entry.binsize, 10000)
        self.assertEqual(entry.file_path, "test/path")
        self.assertEqual(entry.intervals_id, 1)
        self.assertEqual(entry.collection_id, 1)

    def test_entry_updated_if_conflict(self):
        """Tests whether a new entry is added if there is
        no entry in db that satisfies the parameter constraints."""
        # add first entry
        _add_association_data_to_db("test/path", 10000, 1, 1)
        first_id = AssociationIntervalData.query.first().id
        # add second entry
        _add_association_data_to_db("test/path2", 10000, 1, 1)
        self.assertEqual(len(AssociationIntervalData.query.all()), 1)
        entry = AssociationIntervalData.query.first()
        self.assertEqual(first_id, entry.id)
        self.assertEqual(entry.binsize, 10000)
        self.assertEqual(entry.file_path, "test/path2")
        self.assertEqual(entry.intervals_id, 1)
        self.assertEqual(entry.collection_id, 1)


class TestAddStackupToDB(LoginTestCase):
    """Tests for adding stackups to db"""

    def test_add_new_entry_if_no_conflict(self):
        """Tests whether a new entry is added if there is
        no entry in db that satisfies the parameter constraints."""
        _add_stackup_db(
            "test/path",
            "test/pathSmall",
            10000,
            1,
            1
        )
        self.assertEqual(len(IndividualIntervalData.query.all()), 1)
        entry = IndividualIntervalData.query.first()
        self.assertEqual(entry.binsize, 10000)
        self.assertEqual(entry.file_path, "test/path")
        self.assertEqual(entry.file_path_small, "test/pathSmall")
        self.assertEqual(entry.intervals_id, 1)
        self.assertEqual(entry.dataset_id, 1)

    def test_entry_updated_if_conflict(self):
        """Tests whether a new entry is added if there is
        no entry in db that satisfies the parameter constraints."""
        # add first entry
        _add_stackup_db("test/path", "test/pathSmall", 10000, 1, 1)
        first_id = IndividualIntervalData.query.first().id
        # add second entry
        _add_stackup_db("test/path2", "test/pathSmall2", 10000, 1, 1)
        self.assertEqual(len(IndividualIntervalData.query.all()), 1)
        entry = IndividualIntervalData.query.first()
        self.assertEqual(first_id, entry.id)
        self.assertEqual(entry.binsize, 10000)
        self.assertEqual(entry.file_path, "test/path2")
        self.assertEqual(entry.file_path_small, "test/pathSmall2")
        self.assertEqual(entry.intervals_id, 1)
        self.assertEqual(entry.dataset_id, 1)


class TestAddLineToDB(LoginTestCase):
    """Tests for adding line data to db"""

    def test_add_new_entry_if_no_conflict(self):
        """Tests whether a new entry is added if there is
        no entry in db that satisfies the parameter constraints."""
        _add_line_db(
            "test/path",
            10000,
            1,
            1
        )
        self.assertEqual(len(AverageIntervalData.query.all()), 1)
        entry = AverageIntervalData.query.first()
        self.assertEqual(entry.binsize, 10000)
        self.assertEqual(entry.file_path, "test/path")
        self.assertEqual(entry.intervals_id, 1)
        self.assertEqual(entry.dataset_id, 1)
        self.assertEqual(entry.value_type, "line")

    def test_entry_updated_if_conflict(self):
        """Tests whether a new entry is added if there is
        no entry in db that satisfies the parameter constraints."""
        # add first entry
        _add_line_db("test/path", 10000, 1, 1)
        first_id = AverageIntervalData.query.first().id
        # add second entry
        _add_line_db("test/path2", 10000, 1, 1)
        self.assertEqual(len(AverageIntervalData.query.all()), 1)
        entry = AverageIntervalData.query.first()
        self.assertEqual(first_id, entry.id)
        self.assertEqual(entry.binsize, 10000)
        self.assertEqual(entry.file_path, "test/path2")
        self.assertEqual(entry.intervals_id, 1)
        self.assertEqual(entry.dataset_id, 1)
        self.assertEqual(entry.value_type, "line")


class TestAddPileupToDB(LoginTestCase):
    """Tests for adding pileups to db"""

    def test_add_new_entry_if_no_conflict(self):
        """Tests whether a new entry is added if there is
        no entry in db that satisfies the parameter constraints."""
        _add_pileup_db(
            "test/path",
            10000,
            1,
            1,
            "ICCF"
        )
        self.assertEqual(len(AverageIntervalData.query.all()), 1)
        entry = AverageIntervalData.query.first()
        self.assertEqual(entry.binsize, 10000)
        self.assertEqual(entry.file_path, "test/path")
        self.assertEqual(entry.intervals_id, 1)
        self.assertEqual(entry.dataset_id, 1)
        self.assertEqual(entry.value_type, "ICCF")

    def test_entry_updated_if_conflict(self):
        """Tests whether a new entry is added if there is
        no entry in db that satisfies the parameter constraints."""
        # add first entry
        _add_pileup_db("test/path", 10000, 1, 1, "ICCF")
        first_id = AverageIntervalData.query.first().id
        # add second entry
        _add_pileup_db("test/path2", 10000, 1, 1, "ICCF")
        self.assertEqual(len(AverageIntervalData.query.all()), 1)
        entry = AverageIntervalData.query.first()
        self.assertEqual(first_id, entry.id)
        self.assertEqual(entry.binsize, 10000)
        self.assertEqual(entry.file_path, "test/path2")
        self.assertEqual(entry.intervals_id, 1)
        self.assertEqual(entry.dataset_id, 1)
        self.assertEqual(entry.value_type, "ICCF")

if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
