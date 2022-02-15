---
title: "Implementation"
date: 2022-02-11T08:43:32+01:00
draft: true
weight: 3
---

## Architecture overview

In order to provide a reference implementation of the region-set focus approach, we developed HiCognition. HiCognition is a containerized web application that uses a Task-queue in conjunction with multiple workers to allow precomputation of the analysis tasks mentioned. For visualization, HiCognition draws upon powerful javascript frameworks such as [d3.js](https://d3js.org/) and [pixi.js](https://pixijs.com/) to allow the efficient display of the pre-computed data (see the [app architecture section](/docs/development/development_info/) for more details).

## Data management

In order to make managing genomic datasets for exploration practical, HiCognition contains a dataset manager that stores available datasets as well as finished pre-computations in a MySQL database. Here, the user interface of HiCognition provides a separation between genomic regions of interest and genomic features that are available for precomputation, where users can add and view datasets in an interactive table component that allows filtering and editing (see the [data management section](/docs/data_management/) for more details).

## Preprocessing

To select a region-set of interest, the user can submit preprocessing tasks using the preprocessing dialogues and get an overview of running and finished computations via the dataset viewer of the genomic regions. Once a combination of a region-set of interest and a genomic feature has finished its pre-computation, it is available for display.  Here, the region-set focus approach is captured by the layout of the visualisation components (see the [preprocessing section](/docs/preprocessing/) for more details).  


## Visualization

HiCognition uses widget-collections as a container to display specific visualisations. A widget collection has a single region-set that is shared by all its contained widgets. Here, each widget inside a widget collection represents a genomic feature and provides a suitable visualisation for the respective data. A widget collection can contain a variable number of widgets that can be freely arranged to adapt to a specific analysis question. Additionally, widgets of a common type can be linked to share their value-scale to facilitate quantitative comparisons across features or regions (see the [widgets section](/docs/widgets/) for more details).

![Widget concept](/docs/Widget_concept.png)


As genomic data frequently span multiple length-scales, it is important that visualisation concepts adapt to this challenge. HiCognition solves this problem by precomputing a “resolution-stack” of a genomic region-set. Specifically, all preprocessing steps are run with different window sizes and resolutions around the regions of interest, enabling the user to rapidly explore small and large neighbourhoods around the region-set of interest.

![Resolution stack](/docs/resolution_stack.png)

## Sharing data

Finally, HiCognition allows storing particular arrangements of widgets and widget collections as named sessions that can either be reused by the same user later or be shared using a static link to enable anybody to view and reuse a given analysis setup (see the [data sharing section](/docs/sessions/) for more details).

