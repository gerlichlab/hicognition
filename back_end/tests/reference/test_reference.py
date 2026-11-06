"""Compares a fresh run of every preprocessing step with the reference results.

The reference was computed by make_reference.py in the image the lab's instance ran at v0.8.0;
versions.txt beside it lists the libraries. The comparison is by value:

- Cleaned region files, and the errors steps raise, are compared as text.
- Every array has the same shape, its NaNs in the same places, and values within RTOL and ATOL.
- Cluster labels are compared by how well the clusterings agree (adjusted Rand index), since
  a clustering that only numbers its clusters differently is the same clustering.
- Embedding coordinates are compared by how well they keep the distances between regions
  (Spearman correlation of all pairwise distances): UMAP can rotate or mirror an embedding.
- Values that are averages per cluster (2D thumbnails, 1D average values) follow the cluster
  numbering, so only their shapes are kept and compared; the values they average are compared
  directly.

A change that moves results on purpose loosens a tolerance here and says why in the changelog.
"""
import json
import os
import tempfile
import unittest

import numpy as np

from .harness import compute

EXPECTED_DIR = os.path.join(os.path.dirname(__file__), "..", "testfiles", "reference", "expected")
RTOL = 1e-6
ATOL = 1e-12
MIN_ADJUSTED_RAND_INDEX = 0.9
MIN_DISTANCE_CORRELATION = 0.9


def kind(key):
    """How a stored array is compared, from its table and file column."""
    table, column = key.split("/")[0], key.split("/")[-1]
    if column == "cluster_id_path":
        return "clusters"
    if table == "EmbeddingIntervalData" and column == "file_path":
        return "embedding"
    if column in ("thumbnail_path", "feature_distribution_path"):
        return "shape"
    return "values"


class TestReferenceResults(unittest.TestCase):
    """Runs the steps once for all tests; that takes a few minutes."""

    @classmethod
    def setUpClass(cls):
        cls.results = compute(tempfile.mkdtemp(prefix="hicognition-reference-"))
        with np.load(os.path.join(EXPECTED_DIR, "arrays.npz")) as arrays:
            cls.expected_arrays = {key: arrays[key] for key in arrays.files}
        with open(os.path.join(EXPECTED_DIR, "shapes.json"), encoding="utf-8") as f:
            cls.expected_shapes = json.load(f)
        with open(os.path.join(EXPECTED_DIR, "text.json"), encoding="utf-8") as f:
            cls.expected_text = json.load(f)

    def test_same_results_are_stored(self):
        stored = set(self.results)
        expected = set(self.expected_arrays) | set(self.expected_shapes) | set(self.expected_text)
        self.assertEqual(sorted(stored - expected), [], "stored, but not in the reference")
        self.assertEqual(sorted(expected - stored), [], "in the reference, but not stored")

    def test_cleaned_files_and_errors(self):
        for key, text in self.expected_text.items():
            with self.subTest(key=key):
                self.assertEqual(self.results.get(key), text)

    def test_shapes(self):
        for key, shape in self.expected_shapes.items():
            if key in self.results:
                with self.subTest(key=key):
                    self.assertEqual(list(self.results[key].shape), shape)

    def test_arrays(self):
        from scipy.spatial.distance import pdist
        from scipy.stats import spearmanr
        from sklearn.metrics import adjusted_rand_score

        for key, expected in self.expected_arrays.items():
            if key not in self.results:
                continue
            actual = self.results[key]
            with self.subTest(key=key):
                self.assertEqual(actual.shape, expected.shape)
                how = kind(key)
                if how == "values" or np.isnan(expected).all():
                    np.testing.assert_allclose(actual, expected, rtol=RTOL, atol=ATOL, equal_nan=True)
                elif how == "clusters":
                    self.assertGreaterEqual(
                        adjusted_rand_score(expected.ravel(), actual.ravel()), MIN_ADJUSTED_RAND_INDEX
                    )
                elif how == "embedding":
                    np.testing.assert_array_equal(np.isnan(actual), np.isnan(expected))
                    rows = ~np.isnan(expected).any(axis=1)
                    correlation = spearmanr(pdist(expected[rows]), pdist(actual[rows])).correlation
                    self.assertGreaterEqual(correlation, MIN_DISTANCE_CORRELATION)


if __name__ == "__main__":
    unittest.main()
