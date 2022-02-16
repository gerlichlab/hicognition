---
title: "Association"
date: 2022-02-11T09:58:12+01:00
draft: true
tags: ["widgets", "enrichment"]
weight: 6
---
The association widget allows you to determine what other genomic regions are enriched at your target genomic region set. It contains two visualizations that allow you to get an overview of where the most enrichment happens (upper plot) and what exactly is enriched at those sites (lower plot).


![LOLA](/docs/LOLA.png)


## Suitable data

The association widget is suitable for a collection of genomic regions (see [here](TODO) for more information about collections).

## Preprocessing algorithm

### Point-regions

During the preprocessing stage, the [LOLA algorithm](https://pubmed.ncbi.nlm.nih.gov/26508757/) is run for each bin along the specific windowsize. This means that for each bin and candidate region, a contingency tables is built that represent the overlap of the query region (the selected region set), a suitable universe and a candidate target region (one entry in the region collection).

![LOLA workflow](/docs/lola_workflow.jpg)
__Sheffield et al. 2016__

In this preprocessing step, the universe is defined to be all bins of the selected binsize along the entire genome.


### Interval-regions

Preprocessing for interval regions works the same as for point-regions with the exception that the query bins have different sizes and the universe is the union of all query regions.

{{% notice note %}}
The particular selection of the enrichment universe for interval-regions means that enrichment is relative to the selected region-sets! This means that enrichments that are uniform across all selected regions may be lower in magnitude.
{{% /notice %}}

## Visualization

The association widget consists of two main visualizations, the enrichment overview at the top and the ranked enrichments at the bottom. The enrichment overview represents the maximum enrichment at that particular genomic bin amongst all regions in the region-set. It can be thought off as a measure of how much the respective collection exhibits enrichment.

![LOLA enrichment magnitude](/docs/lola_enrichment_magnitude.png)

The overview widget is simultaneously a control point since it allows the selection of the the data to show in the rank plot below. Here, the currently selected bin is highlighted in red and clicking on other bars shifts the selection. The rank-plot below, shows the odds-ratio of the respective members of the selected region collection ranked from lowest to highest. If you hover over one of the points, the name of the respective region set is displayed.

![LOLA rank plot](/docs/lola_rank_plot.png)