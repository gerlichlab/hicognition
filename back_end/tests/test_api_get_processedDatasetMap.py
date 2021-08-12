import unittest
from test_helpers import LoginTestCase

# add path to import app
import sys

sys.path.append("./")
from app import db
from app.models import (
    Dataset,
    Intervals,
    AverageIntervalData,
    IndividualIntervalData,
    Collection,
    AssociationIntervalData,
    EmbeddingIntervalData,
    Task,
)


class TestGetProcessedDatasetMap(LoginTestCase):
    """Tests for /api/datasets/<dataset_id>/processedDatasetMap/ route to list and query sessions."""

    def setUp(self):
        super().setUp()
        # create datasets
        self.owned_bedfile = Dataset(
            id=1,
            user_id=1,
            filetype="bedfile",
            dataset_name="testfile",
            processing_state="finished",
        )
        self.not_owned_bedfile = Dataset(
            id=2,
            user_id=2,
            filetype="bedfile",
            dataset_name="testfile2",
            processing_state="finished",
        )
        self.owned_coolerfile = Dataset(
            id=3,
            user_id=1,
            filetype="cooler",
            dataset_name="testfile3",
            processing_state="finished",
        )
        self.owned_bigwig = Dataset(
            id=4,
            user_id=1,
            filetype="bigwig",
            dataset_name="testfile4",
            processing_state="finished",
        )
        self.owned_datasets = [
            self.owned_bedfile,
            self.owned_coolerfile,
            self.owned_bigwig,
        ]
        self.not_owned_bigwig = Dataset(
            id=5,
            user_id=2,
            filetype="bigwig",
            dataset_name="testfile5",
            processing_state="finished",
        )
        self.not_owned_cooler = Dataset(
            id=6,
            user_id=2,
            filetype="cooler",
            dataset_name="testfile6",
            processing_state="finished",
        )
        self.owned_bedfile2 = Dataset(
            id=7,
            user_id=1,
            filetype="bedfile",
            dataset_name="testfile7",
            processing_state="finished",
        )
        self.owned_bedfile3 = Dataset(
            id=8,
            user_id=1,
            filetype="bedfile",
            dataset_name="testfile8",
            processing_state="finished",
        )
        self.not_owned_datasets = [self.not_owned_bigwig, self.not_owned_cooler]
        # create colledtions
        self.owned_collection = Collection(
            id=1,
            user_id=1,
            name="test_collection",
            datasets=[self.owned_bedfile, self.owned_bedfile2, self.owned_bedfile3],
            processing_state="finished",
        )
        # create intervals
        self.intervals_owned_bedfile = [
            Intervals(id=1, dataset_id=1, windowsize=10000),
            Intervals(id=2, dataset_id=1, windowsize=20000),
            Intervals(id=3, dataset_id=1, windowsize=30000),
        ]
        self.intervals_not_owned_bedfile = [
            Intervals(id=4, dataset_id=2, windowsize=10000),
            Intervals(id=5, dataset_id=2, windowsize=20000),
            Intervals(id=6, dataset_id=2, windowsize=30000),
        ]
        # create pileups
        self.pileups = [
            AverageIntervalData(
                id=1, binsize=1000, dataset_id=3, intervals_id=1, value_type="Obs/Exp"
            ),
            AverageIntervalData(
                id=2, binsize=1000, dataset_id=3, intervals_id=1, value_type="ICCF"
            ),
            AverageIntervalData(
                id=3, binsize=2000, dataset_id=3, intervals_id=2, value_type="Obs/Exp"
            ),
            AverageIntervalData(
                id=4, binsize=2000, dataset_id=3, intervals_id=2, value_type="ICCF"
            ),
            AverageIntervalData(
                id=5, binsize=2000, dataset_id=6, intervals_id=2, value_type="ICCF"
            ),
        ]
        # create line profiles
        self.lineprofiles = [
            AverageIntervalData(
                id=6, binsize=1000, dataset_id=4, intervals_id=1, value_type="line"
            ),
            AverageIntervalData(
                id=7, binsize=2000, dataset_id=4, intervals_id=2, value_type="line"
            ),
            AverageIntervalData(
                id=8, binsize=2000, dataset_id=5, intervals_id=2, value_type="line"
            ),
        ]
        # create stackup
        self.stackups = [
            IndividualIntervalData(id=1, binsize=1000, dataset_id=4, intervals_id=1),
            IndividualIntervalData(id=2, binsize=2000, dataset_id=4, intervals_id=2),
            IndividualIntervalData(id=3, binsize=2000, dataset_id=5, intervals_id=2),
        ]
        # create association data
        self.association_data = [
            AssociationIntervalData(
                id=1, binsize=10000, collection_id=1, intervals_id=1
            ),
            AssociationIntervalData(
                id=2, binsize=20000, collection_id=1, intervals_id=1
            ),
            AssociationIntervalData(
                id=3, binsize=20000, collection_id=1, intervals_id=2
            ),
        ]
        # create embedding data
        self.embedding_data = [
            EmbeddingIntervalData(id=1, binsize=10000, collection_id=1, intervals_id=1),
            EmbeddingIntervalData(id=2, binsize=20000, collection_id=1, intervals_id=1),
            EmbeddingIntervalData(id=3, binsize=20000, collection_id=1, intervals_id=2),
        ]
        # create tasks
        self.processing_bigwig_task = Task(
            id="asdf", dataset_id=self.owned_bigwig.id, complete=False, intervals_id=1
        )
        self.processing_bigwig_task_unused_intervals = Task(
            id="asdf", dataset_id=self.owned_bigwig.id, complete=False, intervals_id=4
        )
        self.completed_bigiwg_task = Task(
            id="asdf1", dataset_id=self.owned_bigwig.id, complete=True, intervals_id=1
        )
        self.processing_cooler_task = Task(
            id="asdf2",
            dataset_id=self.owned_coolerfile.id,
            complete=False,
            intervals_id=1,
        )
        self.processing_cooler_task_unused_intervals = Task(
            id="asdf",
            dataset_id=self.owned_coolerfile.id,
            complete=False,
            intervals_id=4,
        )
        self.completed_cooler_task = Task(
            id="asdf3",
            dataset_id=self.owned_coolerfile.id,
            complete=True,
            intervals_id=1,
        )
        self.processing_collection_task = Task(
            id="asdf4",
            collection_id=self.owned_collection.id,
            complete=False,
            intervals_id=1,
        )
        self.processing_collection_task_unused_intervals = Task(
            id="asdf4",
            collection_id=self.owned_collection.id,
            complete=False,
            intervals_id=4,
        )
        self.completed_collection_task = Task(
            id="asdf5",
            collection_id=self.owned_collection.id,
            complete=True,
            intervals_id=1,
        )

    def test_no_auth(self):
        """No authentication provided, response should be 401"""
        # protected route
        response = self.client.get(
            "/api/datasets/1/processedDataMap/", content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

    def test_404_when_dataset_does_not_exist(self):
        """Test whether route returns 404 if dataset does not exist."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # protected route
        response = self.client.get(
            "/api/datasets/500/processedDataMap/",
            content_type="application/json",
            headers=token_headers,
        )
        self.assertEqual(response.status_code, 404)

    def test_403_if_dataset_is_not_owned(self):
        """Test whether route returns 404 if dataset does not exist."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add datasets
        db.session.add(self.not_owned_bedfile)
        db.session.commit()
        # protected route
        response = self.client.get(
            "/api/datasets/2/processedDataMap/",
            content_type="application/json",
            headers=token_headers,
        )
        self.assertEqual(response.status_code, 403)

    def test_400_if_dataset_is_no_bedfile(self):
        """Test whether route returns 400 if dataset does not a bedfile."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add datasets
        db.session.add(self.owned_coolerfile)
        db.session.commit()
        # protected route
        response = self.client.get(
            "/api/datasets/3/processedDataMap/",
            content_type="application/json",
            headers=token_headers,
        )
        self.assertEqual(response.status_code, 400)

    def test_structure_of_mapping_wo_intervals(self):
        """Test whether the structure of the returned object is correct
        for bedfile without associations."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add datasets
        db.session.add(self.owned_bedfile)
        db.session.commit()
        # protected route
        response = self.client.get(
            "/api/datasets/1/processedDataMap/",
            content_type="application/json",
            headers=token_headers,
        )
        self.assertEqual(response.status_code, 200)
        # check whether response is correct
        expected = {
            "pileup": {},
            "stackup": {},
            "lineprofile": {},
            "lola": {},
            "embedding": {},
        }
        self.assertEqual(response.json, expected)

    def test_structure_of_mapping_w_intervals_wo_data(self):
        """Test whether the structure of the returned object is correct
        for bedfile with intervals that do not contain data."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add datasets
        db.session.add(self.owned_bedfile)
        db.session.add_all(self.not_owned_datasets)
        db.session.add_all(self.intervals_owned_bedfile)
        db.session.commit()
        # protected route
        response = self.client.get(
            "/api/datasets/1/processedDataMap/",
            content_type="application/json",
            headers=token_headers,
        )
        self.assertEqual(response.status_code, 200)
        # check whether response is correct
        expected = {
            "pileup": {},
            "stackup": {},
            "lineprofile": {},
            "lola": {},
            "embedding": {},
        }
        self.assertEqual(response.json, expected)

    def test_structure_of_mapping_w_intervals_w_pileups(self):
        """Test whether the structure of the returned object is correct for
        bedfile associated with pileups"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add datasets
        db.session.add_all(self.owned_datasets)
        db.session.add_all(self.not_owned_datasets)
        db.session.add_all(self.intervals_owned_bedfile)
        db.session.add_all(self.pileups)
        db.session.commit()
        # protected route
        response = self.client.get(
            "/api/datasets/1/processedDataMap/",
            content_type="application/json",
            headers=token_headers,
        )
        self.assertEqual(response.status_code, 200)
        # check whether response is correct
        expected = {
            "pileup": {
                "3": {
                    "name": "testfile3",
                    "data_ids": {
                        "10000": {"1000": {"ICCF": "2", "Obs/Exp": "1"}},
                        "20000": {"2000": {"ICCF": "4", "Obs/Exp": "3"}},
                    },
                }
            },
            "stackup": {},
            "lineprofile": {},
            "lola": {},
            "embedding": {},
        }
        self.assertEqual(response.json, expected)

    def test_structure_of_mapping_w_intervals_w_lineprofiles(self):
        """Test whether the structure of the returned object is correct for
        bedfile associated with pileups"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add datasets
        db.session.add_all(self.owned_datasets)
        db.session.add_all(self.not_owned_datasets)
        db.session.add_all(self.intervals_owned_bedfile)
        db.session.add_all(self.lineprofiles)
        db.session.commit()
        # protected route
        response = self.client.get(
            "/api/datasets/1/processedDataMap/",
            content_type="application/json",
            headers=token_headers,
        )
        self.assertEqual(response.status_code, 200)
        # check whether response is correct
        expected = {
            "pileup": {},
            "stackup": {},
            "lola": {},
            "lineprofile": {
                "4": {
                    "name": "testfile4",
                    "data_ids": {"10000": {"1000": "6"}, "20000": {"2000": "7"}},
                }
            },
            "embedding": {},
        }
        self.assertEqual(response.json, expected)

    def test_structure_of_mapping_w_intervals_w_stackups(self):
        """Test whether the structure of the returned object is correct for
        bedfile associated with pileups"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add datasets
        db.session.add_all(self.owned_datasets)
        db.session.add_all(self.not_owned_datasets)
        db.session.add_all(self.intervals_owned_bedfile)
        db.session.add_all(self.stackups)
        db.session.commit()
        # protected route
        response = self.client.get(
            "/api/datasets/1/processedDataMap/",
            content_type="application/json",
            headers=token_headers,
        )
        self.assertEqual(response.status_code, 200)
        # check whether response is correct
        expected = {
            "pileup": {},
            "stackup": {
                "4": {
                    "name": "testfile4",
                    "data_ids": {"10000": {"1000": "1"}, "20000": {"2000": "2"}},
                }
            },
            "lineprofile": {},
            "lola": {},
            "embedding": {},
        }
        self.assertEqual(response.json, expected)

    def test_structure_of_mapping_w_intervals_w_association_data(self):
        """Test whether the structure of the returned object is correct for
        bedfile associated with pileups"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add datasets
        db.session.add_all(self.owned_datasets)
        db.session.add(self.owned_collection)
        db.session.add_all(self.not_owned_datasets)
        db.session.add_all(self.intervals_owned_bedfile)
        db.session.add_all(self.association_data)
        db.session.commit()
        # protected route
        response = self.client.get(
            "/api/datasets/1/processedDataMap/",
            content_type="application/json",
            headers=token_headers,
        )
        self.assertEqual(response.status_code, 200)
        # check whether response is correct
        expected = {
            "pileup": {},
            "stackup": {},
            "lineprofile": {},
            "lola": {
                "1": {
                    "name": "test_collection",
                    "collection_dataset_names": ["testfile", "testfile7", "testfile8"],
                    "data_ids": {
                        "10000": {"10000": "1", "20000": "2"},
                        "20000": {"20000": "3"},
                    },
                }
            },
            "embedding": {},
        }
        self.assertEqual(response.json, expected)

    def test_structure_of_mapping_w_intervals_w_embedding_data(self):
        """Test whether the structure of the returned object is correct for
        bedfile associated with pileups"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add datasets
        db.session.add_all(self.owned_datasets)
        db.session.add(self.owned_collection)
        db.session.add_all(self.not_owned_datasets)
        db.session.add_all(self.intervals_owned_bedfile)
        db.session.add_all(self.embedding_data)
        db.session.commit()
        # protected route
        response = self.client.get(
            "/api/datasets/1/processedDataMap/",
            content_type="application/json",
            headers=token_headers,
        )
        self.assertEqual(response.status_code, 200)
        # check whether response is correct
        expected = {
            "pileup": {},
            "stackup": {},
            "lineprofile": {},
            "lola": {},
            "embedding": {
                "1": {
                    "name": "test_collection",
                    "collection_dataset_names": ["testfile", "testfile7", "testfile8"],
                    "data_ids": {
                        "10000": {"10000": "1", "20000": "2"},
                        "20000": {"20000": "3"},
                    },
                }
            },
        }
        self.assertEqual(response.json, expected)

    def test_structure_of_mapping_w_intervals_w_all_datatypes(self):
        """Test whether the structure of the returned object is correct for
        bedfile associated with pileups"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add datasets
        db.session.add_all(self.owned_datasets)
        db.session.add_all(self.not_owned_datasets)
        db.session.add(self.owned_collection)
        db.session.add_all(self.intervals_owned_bedfile)
        db.session.add_all(self.pileups)
        db.session.add_all(self.lineprofiles)
        db.session.add_all(self.stackups)
        db.session.add_all(self.association_data)
        db.session.add_all(self.embedding_data)
        db.session.commit()
        # protected route
        response = self.client.get(
            "/api/datasets/1/processedDataMap/",
            content_type="application/json",
            headers=token_headers,
        )
        self.assertEqual(response.status_code, 200)
        # check whether response is correct
        expected = {
            "pileup": {
                "3": {
                    "name": "testfile3",
                    "data_ids": {
                        "10000": {"1000": {"ICCF": "2", "Obs/Exp": "1"}},
                        "20000": {"2000": {"ICCF": "4", "Obs/Exp": "3"}},
                    },
                }
            },
            "stackup": {
                "4": {
                    "name": "testfile4",
                    "data_ids": {"10000": {"1000": "1"}, "20000": {"2000": "2"}},
                }
            },
            "lineprofile": {
                "4": {
                    "name": "testfile4",
                    "data_ids": {"10000": {"1000": "6"}, "20000": {"2000": "7"}},
                }
            },
            "lola": {
                "1": {
                    "name": "test_collection",
                    "collection_dataset_names": ["testfile", "testfile7", "testfile8"],
                    "data_ids": {
                        "10000": {"10000": "1", "20000": "2"},
                        "20000": {"20000": "3"},
                    },
                }
            },
            "embedding": {
                "1": {
                    "name": "test_collection",
                    "collection_dataset_names": ["testfile", "testfile7", "testfile8"],
                    "data_ids": {
                        "10000": {"10000": "1", "20000": "2"},
                        "20000": {"20000": "3"},
                    },
                }
            },
        }
        self.assertEqual(response.json, expected)

    def test_bigwig_dataset_not_sent_when_not_finished(self):
        """Tests whehter only datasets are included in preprocessed dataset map
        that have finished processing for the query region."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add datasets
        db.session.add_all(self.owned_datasets)
        db.session.add_all(self.not_owned_datasets)
        db.session.add(self.owned_collection)
        db.session.add_all(self.intervals_owned_bedfile)
        db.session.add_all(self.pileups)
        db.session.add_all(self.lineprofiles)
        db.session.add_all(self.stackups)
        db.session.add_all(self.association_data)
        db.session.add(self.processing_bigwig_task)
        db.session.add(self.completed_bigiwg_task)
        db.session.add(self.completed_cooler_task)
        db.session.add(self.completed_collection_task)
        db.session.commit()
        # protected route
        response = self.client.get(
            "/api/datasets/1/processedDataMap/",
            content_type="application/json",
            headers=token_headers,
        )
        self.assertEqual(response.status_code, 200)
        # check whether response is correct
        expected = {
            "pileup": {
                "3": {
                    "name": "testfile3",
                    "data_ids": {
                        "10000": {"1000": {"ICCF": "2", "Obs/Exp": "1"}},
                        "20000": {"2000": {"ICCF": "4", "Obs/Exp": "3"}},
                    },
                }
            },
            "stackup": {},
            "lineprofile": {},
            "lola": {
                "1": {
                    "name": "test_collection",
                    "collection_dataset_names": ["testfile", "testfile7", "testfile8"],
                    "data_ids": {
                        "10000": {"10000": "1", "20000": "2"},
                        "20000": {"20000": "3"},
                    },
                }
            },
            "embedding": {}
        }
        self.assertEqual(response.json, expected)

    def test_bigwig_dataset_sent_when_processing_task_of_different_intervals(self):
        """test whether processing tasks associated with different intervals have
        no effect on whether dataset is included."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add datasets
        db.session.add_all(self.owned_datasets)
        db.session.add_all(self.not_owned_datasets)
        db.session.add(self.owned_collection)
        db.session.add_all(self.intervals_owned_bedfile)
        db.session.add_all(self.pileups)
        db.session.add_all(self.lineprofiles)
        db.session.add_all(self.stackups)
        db.session.add_all(self.association_data)
        db.session.add(self.processing_bigwig_task_unused_intervals)
        db.session.add(self.completed_bigiwg_task)
        db.session.add(self.completed_cooler_task)
        db.session.add(self.completed_collection_task)
        db.session.commit()
        # protected route
        response = self.client.get(
            "/api/datasets/1/processedDataMap/",
            content_type="application/json",
            headers=token_headers,
        )
        self.assertEqual(response.status_code, 200)
        # check whether response is correct
        expected = {
            "pileup": {
                "3": {
                    "name": "testfile3",
                    "data_ids": {
                        "10000": {"1000": {"ICCF": "2", "Obs/Exp": "1"}},
                        "20000": {"2000": {"ICCF": "4", "Obs/Exp": "3"}},
                    },
                }
            },
            "stackup": {
                "4": {
                    "name": "testfile4",
                    "data_ids": {"10000": {"1000": "1"}, "20000": {"2000": "2"}},
                }
            },
            "lineprofile": {
                "4": {
                    "name": "testfile4",
                    "data_ids": {"10000": {"1000": "6"}, "20000": {"2000": "7"}},
                }
            },
            "lola": {
                "1": {
                    "name": "test_collection",
                    "collection_dataset_names": ["testfile", "testfile7", "testfile8"],
                    "data_ids": {
                        "10000": {"10000": "1", "20000": "2"},
                        "20000": {"20000": "3"},
                    },
                }
            },
            "embedding": {}
        }
        self.assertEqual(response.json, expected)

    def test_cooler_dataset_sent_when_processing_task_of_different_intervals(self):
        """test whether processing tasks associated with different intervals have
        no effect on whether dataset is included."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add datasets
        db.session.add_all(self.owned_datasets)
        db.session.add_all(self.not_owned_datasets)
        db.session.add(self.owned_collection)
        db.session.add_all(self.intervals_owned_bedfile)
        db.session.add_all(self.pileups)
        db.session.add_all(self.lineprofiles)
        db.session.add_all(self.stackups)
        db.session.add_all(self.association_data)
        db.session.add(self.processing_cooler_task_unused_intervals)
        db.session.add(self.completed_bigiwg_task)
        db.session.add(self.completed_cooler_task)
        db.session.add(self.completed_collection_task)
        db.session.commit()
        # protected route
        response = self.client.get(
            "/api/datasets/1/processedDataMap/",
            content_type="application/json",
            headers=token_headers,
        )
        self.assertEqual(response.status_code, 200)
        # check whether response is correct
        expected = {
            "pileup": {
                "3": {
                    "name": "testfile3",
                    "data_ids": {
                        "10000": {"1000": {"ICCF": "2", "Obs/Exp": "1"}},
                        "20000": {"2000": {"ICCF": "4", "Obs/Exp": "3"}},
                    },
                }
            },
            "stackup": {
                "4": {
                    "name": "testfile4",
                    "data_ids": {"10000": {"1000": "1"}, "20000": {"2000": "2"}},
                }
            },
            "lineprofile": {
                "4": {
                    "name": "testfile4",
                    "data_ids": {"10000": {"1000": "6"}, "20000": {"2000": "7"}},
                }
            },
            "lola": {
                "1": {
                    "name": "test_collection",
                    "collection_dataset_names": ["testfile", "testfile7", "testfile8"],
                    "data_ids": {
                        "10000": {"10000": "1", "20000": "2"},
                        "20000": {"20000": "3"},
                    },
                }
            },
            "embedding": {}
        }
        self.assertEqual(response.json, expected)

    def test_cooler_dataset_not_sent_when_not_finished(self):
        """Tests whehter only datasets are included in preprocessed dataset map
        that have finished processing for the query region."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add datasets
        db.session.add_all(self.owned_datasets)
        db.session.add_all(self.not_owned_datasets)
        db.session.add(self.owned_collection)
        db.session.add_all(self.intervals_owned_bedfile)
        db.session.add_all(self.pileups)
        db.session.add_all(self.lineprofiles)
        db.session.add_all(self.stackups)
        db.session.add_all(self.association_data)
        db.session.add(self.processing_cooler_task)
        db.session.add(self.completed_bigiwg_task)
        db.session.add(self.completed_cooler_task)
        db.session.add(self.completed_collection_task)
        db.session.commit()
        # protected route
        response = self.client.get(
            "/api/datasets/1/processedDataMap/",
            content_type="application/json",
            headers=token_headers,
        )
        self.assertEqual(response.status_code, 200)
        # check whether response is correct
        expected = {
            "pileup": {},
            "stackup": {
                "4": {
                    "name": "testfile4",
                    "data_ids": {"10000": {"1000": "1"}, "20000": {"2000": "2"}},
                }
            },
            "lineprofile": {
                "4": {
                    "name": "testfile4",
                    "data_ids": {"10000": {"1000": "6"}, "20000": {"2000": "7"}},
                }
            },
            "lola": {
                "1": {
                    "name": "test_collection",
                    "collection_dataset_names": ["testfile", "testfile7", "testfile8"],
                    "data_ids": {
                        "10000": {"10000": "1", "20000": "2"},
                        "20000": {"20000": "3"},
                    },
                }
            },
            "embedding": {}
        }
        self.assertEqual(response.json, expected)

    def test_collection_sent_when_processing_task_of_different_intervals(self):
        """test whether processing tasks associated with different intervals have
        no effect on whether dataset is included."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add datasets
        db.session.add_all(self.owned_datasets)
        db.session.add_all(self.not_owned_datasets)
        db.session.add(self.owned_collection)
        db.session.add_all(self.intervals_owned_bedfile)
        db.session.add_all(self.pileups)
        db.session.add_all(self.lineprofiles)
        db.session.add_all(self.stackups)
        db.session.add_all(self.association_data)
        db.session.add(self.processing_collection_task_unused_intervals)
        db.session.add(self.completed_bigiwg_task)
        db.session.add(self.completed_cooler_task)
        db.session.add(self.completed_collection_task)
        db.session.commit()
        # protected route
        response = self.client.get(
            "/api/datasets/1/processedDataMap/",
            content_type="application/json",
            headers=token_headers,
        )
        self.assertEqual(response.status_code, 200)
        # check whether response is correct
        expected = {
            "pileup": {
                "3": {
                    "name": "testfile3",
                    "data_ids": {
                        "10000": {"1000": {"ICCF": "2", "Obs/Exp": "1"}},
                        "20000": {"2000": {"ICCF": "4", "Obs/Exp": "3"}},
                    },
                }
            },
            "stackup": {
                "4": {
                    "name": "testfile4",
                    "data_ids": {"10000": {"1000": "1"}, "20000": {"2000": "2"}},
                }
            },
            "lineprofile": {
                "4": {
                    "name": "testfile4",
                    "data_ids": {"10000": {"1000": "6"}, "20000": {"2000": "7"}},
                }
            },
            "lola": {
                "1": {
                    "name": "test_collection",
                    "collection_dataset_names": ["testfile", "testfile7", "testfile8"],
                    "data_ids": {
                        "10000": {"10000": "1", "20000": "2"},
                        "20000": {"20000": "3"},
                    },
                }
            },
            "embedding": {}
        }
        self.assertEqual(response.json, expected)

    def test_collection_not_sent_when_not_finished(self):
        """Tests whehter only collections are included in preprocessed dataset map
        that have finished processing for the query region."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add datasets
        db.session.add_all(self.owned_datasets)
        db.session.add_all(self.not_owned_datasets)
        db.session.add(self.owned_collection)
        db.session.add_all(self.intervals_owned_bedfile)
        db.session.add_all(self.pileups)
        db.session.add_all(self.lineprofiles)
        db.session.add_all(self.stackups)
        db.session.add_all(self.association_data)
        db.session.add(self.processing_collection_task)
        db.session.add(self.completed_bigiwg_task)
        db.session.add(self.completed_cooler_task)
        db.session.add(self.completed_collection_task)
        db.session.commit()
        # protected route
        response = self.client.get(
            "/api/datasets/1/processedDataMap/",
            content_type="application/json",
            headers=token_headers,
        )
        self.assertEqual(response.status_code, 200)
        # check whether response is correct
        expected = {
            "pileup": {
                "3": {
                    "name": "testfile3",
                    "data_ids": {
                        "10000": {"1000": {"ICCF": "2", "Obs/Exp": "1"}},
                        "20000": {"2000": {"ICCF": "4", "Obs/Exp": "3"}},
                    },
                }
            },
            "stackup": {
                "4": {
                    "name": "testfile4",
                    "data_ids": {"10000": {"1000": "1"}, "20000": {"2000": "2"}},
                }
            },
            "lineprofile": {
                "4": {
                    "name": "testfile4",
                    "data_ids": {"10000": {"1000": "6"}, "20000": {"2000": "7"}},
                }
            },
            "lola": {},
            "embedding": {}
        }
        self.assertEqual(response.json, expected)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
