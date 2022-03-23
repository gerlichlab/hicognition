---
title: "Preprocessing tasks"
date: 2022-02-17T10:19:25+01:00
weight: 1
---

HiCognition provides a number of concrete preprocessing tasks that are related to the abstract tasks defined in the [concepts section](/concepts/region_set_focus/). These can be structured as tasks that aggregate genomic features for a given region set or tasks that aggregate collections of features. The preprocessing tasks are related to the types of [widgets](/widgets/) available for exploration, although some tasks produce data for multiple widgets.

## Tasks for single genomic features

These tasks aggregate a single genomic feature on a genomic region set and thus make this feature available for exploration.

```txt
           is aggregated
feature -------------------> region-set

```

### Aggregate a 1D-feature at a genomic region set

This task produces data for the [1D-average widget](/widgets/lineprofile/) and the [Stacked lineprofile widget](/widgets/stackup/) and amounts to extracting the signal of a biwig file at a genomic region set (see the [widgets](/widgets/) section for a detailed description of the algorithm).

### Aggregate a 2D-feature at a genomic region set

This task produces data for the [2D-average widget](/widgets/2d_average/) and the [2D-feature embedding widget](/widgets/2d_feature_embedding/) and amounts to extracting the signal of a multiresolution cooler file at a genomic region set (see the [widgets section](/widgets/) for a detailed description of the algorithm).


## Tasks for collections of genomic features

These tasks aggregate a collection of genomic features on a genomic region set and make this collection available for exploration.

```txt
feature1 ---
            |
feature2 ---|                       is aggregated
            |------>  Collection -------------------> region-set
    .       |
            |   
featureN ---
```

### Aggregate a 1D-feature collection at a genomic region set

This task produces data for the [1D-feature embedding widget](/widgets/1d_feature_embedding/) and amounts to embedding the genomic region set using the 1D-features into a 2D-space (see the [widgets section](/widgets/) for a detailed description of the algorithm).

### Aggregate a Region collection at a genomic region set

This task produces data for the [Association widget](/widgets/association/) and amounts to running [LOLA](https://pubmed.ncbi.nlm.nih.gov/26508757/) on the region set of interest with the region collection (see the [widgets section](/widgets/) for a detailed description of the algorithm).

## Duration of tasks

A visual exploration tool is only useful if the tasks it fulfills can be completed in a reasonable time. Therefore, we have worked hard on minimizing the required time for each preprocessing step. If you use the default configurations and a machine that complies with our [hardware requirements](/installation/requirements/#hardware), none of the jobs should take longer than ~ 3 minutes. The following table gives a rough estimate of how long different preprocessing steps are expected to run for common input sizes.

| Region size | Preprocessing task                                          | Duration [min] |
|-------------|-------------------------------------------------------------|----------------|
| 1000        | Aggregate a 1D-feature at a genomic region set                    | 0.1            |
| 1000        | Aggregate a 2D-feature at a genomic region set | 0.6 __*__           |
| 1000        | Aggregate a 1D-feature collection at a genomic region set                            | 0.5            |
| 1000        | Aggregate a Region collection at a genomic region set                            | 0.5            |
| 50000       | Aggregate a 1D-feature at a genomic region se                    | 0.5            |
| 50000       | Aggregate a 2D-feature at a genomic region set | 3 __*__             |
| 50000        | Aggregate a 1D-feature collection at a genomic region set                            | 2.5            |
| 50000       | Aggregate a Region collection at a genomic region set                            | 2.5            |

__\*__ *For the Aggregate a 2D-feature at a genomic region set task, the first time you preprocess that particular region, you should expect that it runs ~2x as long as we calculate the Observed/expected values the first time and then cache them for future runs.*

{{% notice warning %}}
If you change the [configuration for windowsizes and binsizes](/installation/configuration/#preprocessing_map), the jobs may take much longer and require more memory.
{{% /notice %}}

That being said, on-demand preprocessing is just one of the potential user flows. We think many preprocessing steps can be submitted in bulk as a large part of exploration tasks involve common "dataset ingredients".

