---
title: "Region-set focus approach"
date: 2022-02-09T15:40:53+01:00
draft: true
weight: 2
---

![Fig1](/docs/Fig2_rsfa.png)

The idea behind the region-set focus approach is that in many biological questions, there is a central region-set that is of particular interest, whereas other genomic data is mainly used to find associations. Specifically, a region-set of interest often arises either because the broad biological question gives a natural constraint (e.g. genes/enhancers in the gene expression field), or a particular experimental procedure produces a new region-set that is not characterised, for example, the set of expressed genes or changed 3d-genome interaction patterns in a perturbation condition. Many analysis questions associated with these region-sets of interest can be abstracted into a small number of tasks that are either associated with testing a specific hypothesis or with generating new hypotheses:

- __Exploring average behaviour__: What is the average magnitude of a specific 1d-/2d-genomic signal?
- __Exploring heterogeneity__ : Is the population of regions homogeneous with respect to a collection of 1d- or 2d-features? What subsets have different behaviour with respect to a collection of 1d- or 2d-features?
- __Enrichment analysis__: What other regions are enriched? 

With an explicit focus on region-sets of interest, these tasks can be formalised to the degree that allows automated precomputation. Here, the user selects a particular region-set and maps genomic features to them by submitting a precomputation job. The particular pre-computation job is dependent on the type of task and the type of genomic feature, where genomic features can either be continuous 1d- or 2d-signals along the genome (for example, a ChIP-seq signal of a particular protein), discrete signals along the genome (for example the binding sites of a protein of interest) or a collection of the above (e.g. the binding sites of chromatin modifiers). The results of these pre-computations can then be explored using visualisation concepts tailored to the type of feature.

An implementation of the region-set focus approach would allow users to complement implicit exploration of genomic features in a track-based browser with explicit analyses separated into the tasks mentioned above. For testing a specific hypothesis, this would allow robust evaluation of average behaviour since appropriate pre-computation and visualisation tools can be employed. When generating new hypotheses about the data, specialised visualisation concepts can help to find robust and complex associations that in turn lead to better hypotheses. Additionally, making these analyses explicit allows storing user sessions and sharing them with collaborators, thereby fostering scientific exchange.
