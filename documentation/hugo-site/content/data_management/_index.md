+++
title = "Data management"
date = 2022-02-04T13:35:46+01:00
weight = 4
chapter = true
pre = "<b>4. </b>"
+++

# Data management

HiCognition is an implementation of the [region-set focus approach](/concepts/region_set_focus/). One central aspect of the application is to allow the management of datasets, both representing genomic regions and features. For more complex analyses, HiCognition also implements managing collections of datasets.

## [Genomic regions](/data_management/regions/)
This chapter describes genomic regions are the central element region-set focus approach in more detail.

## [Genomic features](/data_management/features/)
Genomic features are mainly used to understand genomic regions in the region-set focus approach. They can thus be thought of as “independent variables” that explain the “dependent” genomic regions.

## [Collections](/data_management/collections/)
HiCognition uses collections to group datasets together for them to be available for some of the more complex processing algorithms.

## [Genome assemblies](/data_management/genome_assemblies/)
HiCognition allows managing genome assemblies to work with different assemblies and organisms in parallel. This chapter describes how this is done. 