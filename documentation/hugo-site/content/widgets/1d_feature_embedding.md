---
title: "1D-feature embedding"
date: 2022-02-11T09:56:26+01:00
tags: ["widgets", "1D-features"]
weight: 5
---

The 1D-feature embedding widget can be used to display the distribution of genomic regions with regards to a collection (see [here](TODO) for more details on collections) of 1D-features. It represents a 2-dimensional embedding of the genomic regions as a heatmap of points.

![1d embedding](/docs/1d_embedding.png)

## Suitable data

The 1D-feature embedding widget is suitable for a collection of 1D-features. 1D-features are any genomic dataset that can be represented using a [bigwig file](https://genome.ucsc.edu/goldenpath/help/bigWig.html). This includes coverage tracks for Chip-seq experiments, Gro-seq experiments, but also features derived from Hi-C data such as insulation scores.

## Preprocessing algorithm

### Point-regions

During the preprocessing stage, the value of each 1D-feature at each region (+/- the respective binsize) is extracted and stacked into a feature matrix as follows:

|                  | Feature 1 | ... | Feature k |
|------------------|-----------|-----|-----------|
| __Genomic region 1__ | 0.1       | ... | 1.5       |
| ...              | ...       | ... | ...       |
| __Genomic region n__ | 0.8       | ... | 0.4       |

Where `k` refers to the number of features in the respective 1D-feature collection and `n` refers to the number of genomic regions in the respective region set. Following this step, [umap](https://umap-learn.readthedocs.io/en/latest/) is used with default parameters to get a 2-dimensional embedding of the genomic regions.

Additionally, the regions are clustered using [k-means clustering](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html) into two different cluster-sets (one with a high number of clusters and one with a low number of clusters; see the [configuration section](/docs/installation/configuration) on how to change these numbers). The average magnitude of all features within each cluster is saved and then used to display information thumbnails (see the [visualization section](/docs/widgets/1d_feature_embedding/#visualization) for more details).


### Interval-regions

Interval features are treated exactly as point features, except that instead of the value at the region, the average value over the region defined by the start and end is taken.

## Visualization

The distribution of the genomic regions with regards to a collection of 1D-features is visualized as a 2D-histogram, with the density of points being displayed using a colormap. This widget defines a tooltip that, when hovered over the points, will display the feature distribution for the highlighted cluster.

![1d embedding tooltip](/docs/1d_feature_tooltip.png)

The highlighted clusters are defined as described [above](/docs/widgets/1d_feature_embedding/#point-regions) and the bar plot of the features define the standardized feature values (0 mean and unit variance), with positive values being marked red and negative values being marked blue.

The underlying 1D-features can also be visualized by overlaying the respective values using the overlay controls (see [below](/docs/widgets/1d_feature_embedding/#overlay)). Here, the colormap is switched to represent the selected feature value


![1d feature overlay](/docs/1d_feature_overlay.png)

## Widget controls

The 1D-feature embedding widget defines two controls on the widget and one control on the bar chart tooltip.

### Overlay

The overlay controls, allows the choose a feature from the underlying 1D-feature collection to overlay over the heatmap. To avoid mixing density and overlay magnitude, the average value of the overlayed feature is displayed for each bin. In addition, the default density overlay can also be selected here.

![Overlay option](/docs/Overlay_dialog_1d.png)

### Neighborhood size

One can use the neighborhood size option to choose whether to display large or small clusters (for defining the respective sizes, see the [configuration section](/docs/installation/configuration)) in the barplot tooltip.

![Neighborhood size 1d](/docs/Neighborhood_size_controls_1d.png)


### Create new regions

If one of the highlighted clusters are interesting and you want to further explore them, you can create a new genomic region set just representing the highlighted regions. For this, when the barplot tooltip is shown, click on the "Create new region" button will appear. After clicking that button, a dialog pops up that lets you define the name for your new region set.

![Create new region 1d](/docs/Create_new_region_1d_feature.png)
