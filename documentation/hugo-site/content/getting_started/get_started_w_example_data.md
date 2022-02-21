---
title: "Quick start with example data"
date: 2022-02-03T15:25:44+01:00
---

To take your first steps with HiCognition, you can download example data from our [dropbox location](https://www.dropbox.com/sh/zjfc6sgkbdp3ksh/AAAWrbgKt8hz4npNxSfh-RBja?dl=0). The files located there are centered on analysis that is connected to [sister chromatid sensitive Hi-C](https://doi.org/10.1038/s41586-020-2744-4).

## Example 1: Conformation of sister chromatids around TADs

Needed data:

- `G2_tads_w_size.bed` | The location of TADs in G2 synchronized HeLa cells 
- `G2.fc_1_2_3_4.wOldG2.cis.1000.mcool` | Cis-sister contacts in G2 synchronized HeLa cells
- `G2.fc_1_2_3_4.wOldG2.trans.1000.mcool` | Trans-sister contacts in G2 synchronized HeLa cells

To upload the files, follow our [upload instructions for genomic regions](/docs/data_management/regions/#adding-genomic-regions) and [genomic features](/docs/data_management/features/#adding-genomic-features). The metadata settings are the following:

*TADs:*

- `Perturbation` | none
- `Cell cycle stage` | G2
- `Genome assembly` | hg19
- `Sizetype` | Interval
- `ValueType` | Derived
- `Method` | HiC

*Cooler files:*

- `Perturbation` | none
- `Cell cycle stage` | G2
- `Genome assembly` | hg19
- `ValueType` | Interaction
- `Method` | HiC
- `Normalization` | ICCF

{{% notice note %}}
The .mcool files are quite big and you should expect them to take a few minutes to upload (depending on your internet connection).
{{% /notice %}}

Once the files are uploaded, start preprocessing the two 2D-features at TAD-boundaries by following our [preprocessing guide](/docs/preprocessing/manage_preprocessing/). Once preprocessing is finished, you can create a widget collection by clicking on the <img src="/docs/plus_button.png" class="inline-picture"> at the bottom right of the HiCognition start page. This will create an empty widget collection:

<img src="/docs/Widget_collection.png" class="half-width">

By clicking on the region-controls, you can select your TADs as a region. Once that is done, hover over the center +-icon to reveal the widget-type menu:

<img src="/docs/Select_2d_average.png" class="quarter-width">

Once you selected the 2D-average widget, you can select one of the two 2D-features that you added. For example, if you select the cis-sister contacts, your widget collection should look like this:

<img src="/docs/2d-average-w-cis.png" class="quarter-width">

This picture represents the average behavior of cis-sister contacts around TADs. You can then resize your widget collection to add trans-sister contacts as a second widget. The resulting collection should look like this:

<img src="/docs/2d-average-cis-and-trans.png" class="half-width">

This view now represents the average behavior of cis-sister and trans-sister contacts around TAD-boundaries. If you want to look at the heterogeneity of e.g. trans-sister contacts around TADs, you can resize your widget collection to add a new slot and fill it with a 2D-embedding widget:


<img src="/docs/Add_2d_embedding.png" class="half-width">

Once you added the widget, you can select the trans-sister contacts as features to display. Your widget-collection should now look like this:

<img src="/docs/2d-embedding-tads.png" class="half-width">

The 2D-embedding widget now allows you to look at the heterogeneity of trans-sister contacts at TADs (see the [section about this widget](/docs/widgets/2d-embedding) for more details).


