---
title: "1D-average"
date: 2022-02-11T09:56:01+01:00
draft: true
weight: 1
---

The 1D-average widget can be used to display the average magnitude of a 1D-genomic feature over a specific region set. It is a simple line-profile visualization that can load one or more genomic datasets and implements simple tooltip that shows the magnitude of the specific data sets.

![Widget concept](/docs/lineprofile_widget.png)

## Suitable data

The 1D-average widget is suitable for any genomic dataset that can be represented using a [bigwig file](https://genome.ucsc.edu/goldenpath/help/bigWig.html). This includes coverage tracks for Chip-seq experiments, Gro-seq experiments, but also features derived from Hi-C data such as insulation scores.

## Preprocessing algorithm

### Point-regions

During the preprocessing stage, snippets are extracted from the respective bigwig file for each entry in the genomic region set, with different window sizes. These snippets are stacked row-wise into a matrix and reduced column-wise to produce a single value per bin.

### Interval-regions

During the preprocessing stage, snippets are extracted from the respective bigwig file for each entry in the genomic region set. In contrast to th point-region preprocessing, the snippets are defined by each regio's start and end. Before stacking, each snippet is scaled to have the same number of bins. Then they are stacked row-wise into a matrix and reduced column-wise to produce a single value per bin.

## Visualization

The 1D-average widget displays aggregated data sets as a lineprofile, which plots the specific value for a genomic bin, against its relative position with regards to the center. If you hover over the widget, a tooltip is displayed that reads the magnitude of the respective lines. 

## Widget controls

The 1D-average widget has a single widget control option, which allows user normalize the displayed data to lie between 0 and 1. This is helpful when comparing multiple features.

![Widget controls](/docs/lineprofile_widget_widget_controls.png)