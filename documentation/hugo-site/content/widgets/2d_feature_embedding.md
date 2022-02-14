---
title: "2D-feature embedding"
date: 2022-02-11T09:56:29+01:00
draft: true
tags: ["widgets", "2D-features"]
weight: 5
---

The 2D-feature embedding widget can be used to display the distribution of genomic regions with regards to a 2D-genomic feature. It represents a 2-dimensional embedding of the genomic regions as a heatmap of points.

![2d embedding](/docs/2d_feature_embedding.png)


## Suitable data

The 2D-feature embedding widget is suitable for any genomic dataset that can be represented using a multiresolution [cooler file](https://cooler.readthedocs.io/en/latest/). This is mostly suitable for Hi-C data, but can also include other data sets that assign a value to a tuple of genomic coordinates.


## Preprocessing algorithm

In general, the preprocessing for data to be displayed in the 2D-feature embedding widget happens together with preprocessing for the [2D-average widget](/docs/widgets/2d_average/) and thus many of the steps are shared.


### Point-regions

During the preprocessing state, snippets of the underlying interaction matrix are extracted from the mcool file for each entry in the genomic region set, with different window sizes. Then, these images are downsampled and flattened into a "feature-representation". The resulting feature matrix has the following shape:

|                  | Image feature 1 | ... | Image feature k |
|------------------|-----------|-----|-----------|
| __Genomic region 1__ | 0.1       | ... | 1.5       |
| ...              | ...       | ... | ...       |
| __Genomic region n__ | 0.8       | ... | 0.4       |

Where `k` refers to the number of pixels in the downsampled images and `n` refers to the number of genomic regions in the respective region set. Following this step, [umap](https://umap-learn.readthedocs.io/en/latest/) is used with default parameters to get a 2-dimensional embedding of the genomic regions.

Additionally, the regions are clustered using [k-means clustering](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html) into two different cluster-sets (one with a high number of clusters and one with a low number of clusters; see the [configuration section](/docs/installation/configuration) on how to change these numbers). A cluster "thumbnail" that represents the average image within this cluster is saved and then used to display information thumbnails (see the [visualization section](/docs/widgets/1d_feature_embedding/#visualization) for more details).

### Interval-regions

Interval features are treated exactly as point features, except that images are scaled to a common size before processing.

## Visualization

The distribution of the genomic regions with regards to a 2D-feature is visualized as a 2D-histogram, with the density of points being displayed using a colormap. This widget defines a tooltip that, when hovered over the points, will display a cluster thumbnail that represents the average image within that cluster.

![2d embedding tooltip](/docs/2d_feature_embedding_tooltip.png)


## Widget controls

The 2D-feature embedding widget defines four controls on the widget and one control on the thumbnail tooltip.

### Sharing 

The sharing controls allows you to select whether all thumbnail representations should share a common color scale or not.

![2d feature value scale](/docs/2d_feature_value_scale.png)


### Scale

The scale widget control allows to switch between ICCF values (__I__ teratively __C__ orrected __C__ ontact __F__ requency) and Observer/expected values, which were normalized to the genome-wide, distance dependent decay of contact frequency.

### Transform

The transform widget control allows you select whether the values displayed in the thumbnails should be log-transformed or not.

### Neighborhood size

One can use the neighborhood size option to choose whether to display large or small clusters (for defining the respective sizes, see the [configuration section](/docs/installation/configuration)) in the thumbnail tooltip.


### Create new region

If one of the highlighted clusters are interesting and you want to further explore them, you can create a new genomic region set just representing the highlighted regions. For this, when the thumbnail tooltip is shown, click and the "Create new region" button will appear. After clicking that button, a dialog pops up that lets you define the name for your new region set.

![2d feature create new region](/docs/2d_feature_create_new_region.png)
