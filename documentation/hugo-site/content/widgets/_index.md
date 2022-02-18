+++
title = "Widgets"
date = 2022-02-03T15:35:17+01:00
weight = 6
chapter = true
pre = "<b>6. </b>"
+++

# Widgets

HiCognition implements the region-set focus approach (see the [concept section](/docs/concept/region_set_focus/) for details) on a visualization level using widget collections and widgets. Widget collections represent a single set of genomic regions (e.g. Chip-Seq peaks of a target protein) and can host one or more widgets that represent genomic features (e.g. Chip-Seq tracks or Hi-C tracks).

![Widget concept](/docs/Widget_concept.png)

Features are linked to genomic regions via preprocessing steps (see the [preprocessing section](/docs/preprocessing/) for more details), which mostly represent data aggregation. Once preprocessing has linked features to genomic regions, they are available for addition to a widget collection via appropriate widgets (see the [widget controls section](/docs/widgets/widget_controls) on how to do that).

HiCognition implements preprocessing to allow answering three main questions at a genomic region set (see the [concept section](/docs/concept/region_set_focus/) for more details):

1. __Exploring average behaviour__: What is the average magnitude of a specific 1d-/2d-genomic signal?
2. __Exploring heterogeneity__ : Is the population of regions homogeneous with respect to a collection of 1d- or 2d-features? What subsets have different behaviour with respect to a collection of 1d- or 2d-features?
3. __Enrichment analysis__: What other regions are enriched? 

The results of these preprocessing steps can be visualized using specific widgets:

## [1D-average widget](/docs/widgets/lineprofile/)

Allows to assess what the average magnitude of a 1d-genomic signal is at a genomic region set

## [2D-average widget](/docs/widgets/2d_average/)

Allows to assess what the average magnitude of a 2d-genomic signal is at a genomic region set

## [Stacked lineprofile widget](/docs/widgets/stackup/)

Allows to assess whether a population of regions is homogeneous with regards to a 1d-genomic signal 

## [1D-feature embedding widget](/docs/widgets/1d_feature_embedding/)

Allows to assess whether a population of regions is homogeneous with regards to a set of 1d-genomic signals 

## [2D-feature embedding widget](/docs/widgets/2d_feature_embedding/)

Allows to assess whether a population of regions is homogeneous with regards to a 2d-genomic signal 

## [Association widget](/docs/widgets/association/)

Allows to assess what other regions overlap with a set of genomic regions 
