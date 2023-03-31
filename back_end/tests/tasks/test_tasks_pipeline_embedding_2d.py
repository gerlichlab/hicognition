"""Module with the tests for the 2D-data embedding preprocessing realted tasks."""
import unittest
import numpy as np
from tests.test_utils.test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
# import sys
# sys.path.append("./")
from app.pipeline_worker_functions import _do_embedding_2d


class TestEmbedding2DWorkerFunction(LoginTestCase, TempDirTestCase):
    """Tests ebmedding2d worker function"""

    def test_output_correct_shapes(self):
        """tests whether the produced outputs have correct shape"""
        # mock stuff
        array = np.stack([np.random.normal(size=(10, 10)) for i in range(20)], axis=2)
        # make call
        embedding_results = _do_embedding_2d(array)
        self.assertEqual(embedding_results["embedding"].shape, (20, 2))
        self.assertEqual(
            embedding_results["clusters"]["large"]["cluster_ids"].shape, (20,)
        )
        self.assertEqual(
            embedding_results["clusters"]["small"]["cluster_ids"].shape, (20,)
        )
        self.assertEqual(
            embedding_results["clusters"]["large"]["thumbnails"].shape, (20, 10, 10)
        )
        self.assertEqual(
            embedding_results["clusters"]["small"]["thumbnails"].shape, (10, 10, 10)
        )

    def test_output_correct_shapes_if_feature_extraction_fails(self):
        """tests whether the produced outputs have correct shape"""
        # mock stuff
        array = np.stack([np.full((10, 10), np.nan) for i in range(20)], axis=2)
        # make call
        embedding_results = _do_embedding_2d(array)
        self.assertEqual(embedding_results["embedding"].shape, (20, 2))
        self.assertEqual(
            embedding_results["clusters"]["large"]["cluster_ids"].shape, (20,)
        )
        self.assertEqual(
            embedding_results["clusters"]["small"]["cluster_ids"].shape, (20,)
        )
        self.assertEqual(
            embedding_results["clusters"]["large"]["thumbnails"].shape, (20, 10, 10)
        )
        self.assertEqual(
            embedding_results["clusters"]["small"]["thumbnails"].shape, (10, 10, 10)
        )


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
