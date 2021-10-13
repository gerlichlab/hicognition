"""Tests for io_helpers.py."""
import unittest
import numpy as np
from hicognition import feature_extraction


class TestExtractImageFeatures(unittest.TestCase):
    """Tests for function to extract image features"""

    @classmethod
    def setUp(self):
        array = np.empty((100, 100))
        array.fill(np.nan)
        self.nan_array = array

    def test_empty_input_returns_none(self):
        """tests whether calling with empty input returns None"""
        result = feature_extraction.extract_image_features([])
        self.assertEqual(result, None)

    def test_array_of_nans_does_not_cause_error(self):
        """Tests whether supplying an array of only nans
        results in correct output (all 0s because sato turns nan into 0)."""
        result = feature_extraction.extract_image_features([self.nan_array])
        self.assertEqual(result, None)

    def test_random_arrays_return_right_shape(self):
        """Tests whether random arrays return right shape"""
        images = [np.random.normal(0, 1, (10, 10)) for i in range(5)]
        result = feature_extraction.extract_image_features(images)
        self.assertEqual(result.shape, (5, 100))

    def test_heterogenous_random_arrays_return_right_shape(self):
        """Tests whether random arrays return right shape"""
        images = [np.random.normal(0, 1, (i, i)) for i in range(5)]
        result = feature_extraction.extract_image_features(images)
        self.assertEqual(result.shape, (5, 100))

    def test_correct_arrays_returned(self):
        """Test whether correct array is returned for small example"""
        images = [
            np.array([[1, 2], [5, 6]]),
            np.array([[8, 9], [1, 1]]),
            np.array([[100, 1], [87, 2]]),
        ]
        result = feature_extraction.extract_image_features(images, (1, 1))
        expected = np.array([[-0.74355736], [-0.67001872], [1.41357609]])
        self.assertTrue(np.allclose(result, expected))


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
