---
title: "Stacked lineprofiles"
date: 2022-02-11T09:56:17+01:00
draft: true
tags: ["widgets", "1D-features"]
weight: 3
---

The stacked lineprofile widget can be used to display individual examples of 1D-genomic features over a specific region set. It is a heatmap representation, where each row corresponds to one genomic region.

{{% notice note %}}
The stacked lineprofile widget does not show the entirety of the selected region-set, but only a subset. The down-sampling ratio can be defined as configuration variable (see the [configuration section](/docs/installation/configuration) for details)
{{% /notice %}}

![Stackup](/docs/stackup.png)

## Suitable data

The stacked lineprofile widget is suitable for any genomic dataset that can be represented using a [bigwig file](https://genome.ucsc.edu/goldenpath/help/bigWig.html). This includes coverage tracks for Chip-seq experiments, Gro-seq experiments, but also features derived from Hi-C data such as insulation scores.

## Preprocessing algorithm

The preprocessing algorithms are very similar to the any applied with data suitable for the [1D-average widget](/docs/widgets/widgets/lineprofile/)

### Point-regions


During the preprocessing stage, snippets are extracted from the respective bigwig file for each entry in the genomic region set, with different window sizes. These snippets are then stacked row-wise into a matrix

### Interval-regions

During the preprocessing stage, snippets are extracted from the respective bigwig file for each entry in the genomic region set. In contrast to the point-region preprocessing, the snippets are defined by each region's start and end. Before stacking, each snippet is scaled to have the same number of bins.

## Visualization

The stacked lineprofile widget displays aggregated data sets as a heatmap. The color scale used to display the values is dynamic and can be adjusted with the sliders at the top and bottom of the colorbar.

## Widget controls

The stacked lineprofile widget defines two widget controls, one for specifying the sort order of the rows and the other for sharing value scales between widgets.

### Sort order

The sort order widget control option allows to specify by which values to sort and whether to sort in an ascending of descending fashion.

![Stackup sort order](/docs/stackup_sort_order.png)

For point-regions, the sort values are the following:

- __Center column__ | sort by the center column
- __Random__ | shuffle rows

For interval-regions, the sort values are the following:

- __Region__ | sort by average value of the continued region (between start and end)
- __Left boundary__ | sort by left boundary
- __Right boundary__ | sort by right boundary
- __Random__ | shuffle rows

### Sharing

The stacked lineprofile widget supports sharing value scales in a similar fashion to the [2d-average widget](/docs/widgets/2d_average/#share-value-scale). In addition, the stacked lineprofile widget allows to share sort-order between widgets that reside in the same widget collection. For this, click on "Take sort order from" on then click on the traget widget

![Stackup sort order controls](/docs/stackup_sort_order_sharing_controls.png)

After that, a colored line under the stacked lineprofile indicates that the two widgets are linked. The sort order donor has a continuous colored line, whereas the sort order acceptor has a dashed colored line.

![Stackup sort order sharing](/docs/stackup_sort_order_sharing.png)

The sort order acceptance widgets can now no longer change their sort orders and their sort order is set to shared.

![Stackup sort order sharing controls](/docs/stackup_sort_order_shared_controls.png)

When the sort order is changed on the donor widget, however, all acceptor widgets follow suite. You can link multiple widgets together by taking the sort order of a shared donor. You can also link multiple widgets independently, which then are marked by differently colored color lines.

![Multiple sort order sharing](/docs/Multiple_sort_order_sharing.png)


If you want to stop sharing sort order, you can select "Release sort order" on the sort order acceptor.