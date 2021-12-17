"""Module to extract features from genomic datasets"""

import cv2
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
import numpy as np


def _downscale_images(
    images, blurring_kernel_size, blurring_kernel_sigma, pixel_target
):
    pixel_features = []
    for temp_image in images:
        pixel_features.append(
            cv2.resize(
                cv2.GaussianBlur(
                    temp_image,
                    (blurring_kernel_size, blurring_kernel_size),
                    blurring_kernel_sigma,
                ),
                pixel_target
            ).flatten()
        )
    return pixel_features


def _upscale_images(images, pixel_target):
    pixel_features = []
    for temp_image in images:
        pixel_features.append(cv2.resize(temp_image, pixel_target).flatten())
    return pixel_features


def extract_image_features(images, pixel_target=(10, 10)):
    """Implementation of extract image features using opencv"""
    if len(images) == 0:
        return None
    # replace empty arrays and arrays with single element with nans
    images = [
        image if len(image) > 1 else np.full((10, 10), np.nan) for image in images
    ]
    # check whether downsampling needs to be applied
    if images[0].shape[0] < pixel_target[0]:
        downsampling = False
    else:
        downsampling = True
        downsampling_factor = images[0].shape[0] // pixel_target[0]
        blurring_kernel_sigma = (downsampling_factor - 1) // 2
        blurring_kernel_size = (blurring_kernel_sigma * 4) + 1
    # calculate features
    pixel_features = (
        _downscale_images(
            images, blurring_kernel_size, blurring_kernel_sigma, pixel_target
        )
        if downsampling
        else _upscale_images(images, pixel_target)
    )
    X = np.stack(pixel_features)
    # replace inf with nan
    X[np.isinf(X)] = np.nan
    # is all none return None
    if np.all(np.isnan(X)):
        return None
    imputed = SimpleImputer().fit_transform(X)
    scaled = StandardScaler().fit_transform(imputed)
    return scaled