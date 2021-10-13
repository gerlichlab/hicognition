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
        expected = np.zeros(
            (1, 100)
        )  # this is 100 because all features except to sobel ones are 0 and are removed by simple imputer
        self.assertTrue(np.allclose(result, expected))

    def test_random_arrays_return_right_shape(self):
        """Tests whether random arrays return right shape"""
        images = [np.random.normal(0, 1, (10, 10)) for i in range(5)]
        result = feature_extraction.extract_image_features(images)
        self.assertEqual(result.shape, (5, 500))

    def test_heterogenous_random_arrays_return_right_shape(self):
        """Tests whether random arrays return right shape"""
        images = [np.random.normal(0, 1, (i, i)) for i in range(5)]
        result = feature_extraction.extract_image_features(images)
        self.assertEqual(result.shape, (5, 500))

    def test_correct_arrays_returned(self):
        """Test whether correct array is returned for small example"""
        images = [
            np.array([[1, 2], [5, 6]]),
            np.array([[8, 9], [1, 1]]),
            np.array([[100, 1], [87, 2]]),
        ]
        result = feature_extraction.extract_image_features(images, (1, 1))
        expected = np.array(
            [
                [-0.73744372, 1.40399977, 0.71281686, -0.78406256, 0.0],
                [-0.6763296, -0.84893009, 0.70138129, -0.62725005, 0.0],
                [1.41377333, -0.55506968, -1.41419815, 1.41131261, 0.0],
            ]
        )
        self.assertTrue(np.allclose(result, expected))


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
