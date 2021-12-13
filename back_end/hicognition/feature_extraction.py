"""Module to extract features from genomic datasets"""

from skimage.transform import resize
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
import numpy as np


def extract_image_features(images, pixel_target=(10, 10)):
    """Takes an iterable of images, as well as a shape of the form (rows, columns)
    and applies a series of filters to the smoothed input image, before resizing the ouptut to
    the sizes specified in pixel_target. Scales and imputes the features. Returns a
    numpy array of the size (number images, number features)"""
    if len(images) == 0:
        return None
    # replace empty arrays and arrays with single element with nans
    images = [image if len(image) > 1 else np.full((10, 10), np.nan) for image in images]
    # calculate features
    pixel_features = []
    for temp_image in images:
        pixel_features.append(resize(temp_image, pixel_target).flatten())
    X = np.stack(pixel_features)
    # replace inf with nan
    X[np.isinf(X)] = np.nan
    # is all none return None
    if np.all(np.isnan(X)):
        return None
    imputed = SimpleImputer().fit_transform(X)
    scaled = StandardScaler().fit_transform(imputed)
    return scaled