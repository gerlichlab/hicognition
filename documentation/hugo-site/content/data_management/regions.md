---
title: "Regions"
date: 2022-02-16T10:09:52+01:00
weight: 1
draft: true
---

Genomic regions are the central element of the [region-set focus approach](/docs/concept/region_set_focus/) and are represented in practice by `BED` files that the user uploads to the server.

## Data requirements

BED-files should conform to the [BED-standard](https://genome.ucsc.edu/FAQ/FAQformat.html), meaning that the should contain all __required__ BED fields with __tab-separated__ entries:

1. `chrom`
2. `chromStart`
3. `chromEnd`

BED-files that are accepted by HiCognition may contain column names, so the following is acceptable:

```txt
chrom   start   end
chr1    1234    5678
.       .       .
.       .       .   
.       .       .
```

In addition, BED-files can contain comment lines (containing a leading `#`) as well as `track` and `browser` lines. So the following would be an acceptable file:

```txt
# This is my favorite file
track name=pairedReads description="Clone Paired Reads" useScore=1
chr22 1000 5000 cloneA 960 + 1000 5000 0 2 567,488, 0,3512
chr22 2000 6000 cloneB 900 - 2000 6000 0 2 433,399, 0,3601
```

A requirement that you are responsible for yourself is that the BED-file conforms to the selected genome assembly (see the [genome assemblies section](/docs/data_management/genome_assemblies/) for more information). HiCognition won't crash when doing preprocessing using a BED-file with chromosomes that are not in your selected genome assembly, but will emit blank data for those regions. But we cannot check whether positions within the bounds of a given assembly are derived from that assembly!

{{% notice warning %}}
Always check that your BED-file contains coordinates that fit the selected genome assembly!
{{% /notice %}}



## Types of genomic regions

HiCognition supports two different types of genome regions that will be preprocessed and displayed in different ways. For a description of how the different visualizations adapt to the different types of genomic regions, see the [widget section](/docs/widgets/).

### Point regions

Point regions are treated by HiCognition as points in the genome. This means that internally, the `start` and `end` field in your uploaded BED-file will be collapsed into a single position that represents the center of that region. This region type is suitable when the features that you look at likely have no internal structure through the span of your regions. Examples here are Chip-seq peaks of transcription factors, transcriptional start sites of genes or boundaries of topologically associating domains.

When working with point regions, HiCognition will create views with different windowsizes around these point regions to allow exploration of multiple length-scales.

```txt
Windowsize
                                         Point     
   Small                              -----|-----
     |
     |                                   Point     
     |                       --------------|--------------
     |
     |                                   Point                
     |                 --------------------|--------------------
     |
     v                                   Point                
   Large       ----------------------------|----------------------------
```

To reduce computational load, the binsizes at which features are aggregated get smaller when windowsizes get larger. The particular setting can be changed in the configuration files of HiCognition (see the [configuration section](/docs/installation/configuration/) for more details).

### Interval regions

Interval regions are treated by HiCognition as regions that have a meaningful start, end and with that size in the genome. This region type is suitable when the features that you look at likely have internal structure through the span of your regions. Treating regions as interval regions is also useful when they have differing sizes and you want to look at features without regard for the size of the region. This is because all preprocessing steps for interval regions change the coordinate system from genomic coordinates to relative coordinates with relation to the size of the regions.

The binsizes that are used to aggregate features are thus defined as percentage of the interval size. Practically, this means that if you have a particular region that is 1 Mbp in size and another region that is 500 kbp in size, the effective binsize (at 1 %) for the former will be 10 kbp and for the latter 5 kbp. This also means that we interpolate genomic features to fit the target binsize. This is convenient to exclude size effects, but can introduce artefacts. So always have that in mind when exploring interval features!

{{% notice warning %}}
Interval regions will cause genomic features to be scaled to a common size. This can introduce artefacts!
{{% /notice %}}

Interval regions are displayed with a little expansion left and right to be able to compare them to a potential baseline:

```txt
Left Expansion                 Region             Right Expansion
---------------|---------------------------------|---------------
```

See the [configuration section](/docs/installation/configuration/#variable_size_expansion_factor) for how to set the extent of the expansion.

## Description of genomic regions

In order to allow efficient filtering and searching as well as easier display of genomic regions, we defined a formal description of genomic region sets that is exposed to the user both when adding new regions and when viewing genomic regions. The structure of the description fields of a genomic region set can be seen in the following graph:

![region graph](/docs/region_metadata.png)

In this graph, all nodes that represent a value that the user can select are represented as red. If the selection of the user can lead to different selections lower in the graph, these options are displayed as black nodes. The first children of `Region` are fields that need to be defined for all region sets and have no influence on the later selection hierarchy:

- __Assembly__ | The genome assembly this region set belongs to
- __Perturbation__ | The perturbation condition (or none) that was used in the experiment that led to this dataset
- __CellCycleStage__ | The cell cycle stage the cells were in when the data was collected
- __SizeType__ | Which sizetype (see [above](/docs/data_management/regions/#types-of-genomic-regions)) the genomic regions should be treated as

Then, the `ValueType` needs to be selected. This describes what kind of genomic regions this dataset are, this can be one of the following:

- __Peak__ | A peak from an experiment that produces continuous genomic data e.g. ChiP-Seq
- __GenomeAnnotation__ | A genomic region set that is obtained by integrating multiple data sources and human intervention (e.g. genes, transcriptional start sites etc.)
- __Derived__ | If regions have been derived from a single other dataset (e.g. TADs derived from a Hi-C experiment)

Selection of a specific `ValueType` leads to different required metadata downstream. E.g. if the `ValueType` is `Peak` than the possible selection of methods is different than when the `ValueType` is `Derived`.


## Adding genomic regions

Adding genomic regions can be done by uploading a BED-file and filling out the required metadata field. This can be done for single files, or when you have multiple files using the bulk addition option.


### Single addition

To add a single genomic region set, open the side drawer and click on the add region button:

![add single region start dialogue](/docs/add_single_region_menu.png)

Then, a dialog will pop up where you can select a region file, specify its name and select a genome assembly.

![add single region dialogue](/docs/add_single_region_unselected.png)

When you added the BED-file, options will appear that encapsulate the hierarchical structure describe [above](/docs/data_management/regions/#description-of-genomic-regions)

![additional options single addition](/docs/additional_options_single_addition.png)

Once you are happy with your selection, you can hit submit and your dataset will be uploaded!

### Bulk addition

If you want to add multiple genomic regions, you can use the bulk addition option:

![bulk addition](/docs/bulk_addition.png)

Bulk addition is organized as a stepper, where you add the same information as in the [single addition](/docs/data_management/regions/#single-addition) at the different positions of the stepper.

## Managing genomic regions

Managing genomic regions is done using a central table component that can be opened in the data management sidebar:

![open dataset table](/docs/open_dataset_table.png)

### Viewing

When you click on the `Show Regions` button, a table dialogue opens that shows you all available genomic region sets:

![region dataset table](/docs/region_dataset_table.png)

This top-row of this view allows you to select a specific genome assembly and contains a search field that allows for quick filtering of interesting datasets. For more fine grained control over the filtering process, you can expand the filter box, which displays the description fields mentioned [above](/docs/data_management/regions/#description-of-genomic-regions).

![filter options dataset table](/docs/filter_options_dataset_table.png)

Per default, only a subset of fields are displayed, but you change this in the fields box:

![field selection dataset table](/docs/field_selection_dataset_table.png)

All interfaces in HiCognition that need dataset selection use this table component.

### Editing

You can edit the description fields and name of a dataset, by selecting it in the table component, and then hitting the `Edit` button. This will display the edit dialogue:


![edit form](/docs/edit_form.png)

Here you can edit most description fields and once you are finished, you can hit `Submit Dataset` to save your changes.

{{% notice tip %}}
The only parameter you cannot edit is the `SizeType` field as this would invalidate prior preprocessing done on the dataset.
{{% /notice %}}

### Deleting

You can delete datasets by selecting them in the table component, and then hitting the `Delete` button. Note that you can only delete a dataset when you are its owner, not when it has been shared (see the [dataset sharing section](/docs/sessions/) for more information) with you.

{{% notice warning %}}
Deleting a dataset will cause all preprocessing data to be lost. Be careful!
{{% /notice %}}