"""Module to extract features from genomic datasets"""

from skimage.transform import resize
from skimage.filters import sobel_h, sobel_v, sato, hessian, gaussian
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
    images = [image if len(image) > 1 else np.empty((10, 10)) for image in images]
    # calculate features
    smoothed = [gaussian(temp_image) for temp_image in images]
    pixel_features = [resize(example, pixel_target).flatten() for example in smoothed]
    sobel_h_features = [
        resize(sobel_h(example), pixel_target).flatten() for example in smoothed
    ]
    sobel_v_features = [
        resize(sobel_v(example), pixel_target).flatten() for example in smoothed
    ]
    sato_features = [
        resize(sato(example, mode="reflect"), pixel_target).flatten()
        for example in smoothed
    ]
    hess_features = [
        resize(hessian(example, mode="reflect"), pixel_target).flatten()
        for example in smoothed
    ]
    feature_list = [
        np.concatenate(zipped_features)
        for zipped_features in zip(
            pixel_features,
            sobel_h_features,
            sobel_v_features,
            sato_features,
            hess_features,
        )
    ]
    X = np.stack(feature_list)
    imputed = SimpleImputer().fit_transform(X)
    scaled = StandardScaler().fit_transform(imputed)
    return scaled