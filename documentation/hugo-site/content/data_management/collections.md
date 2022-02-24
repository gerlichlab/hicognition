---
title: "Collections"
date: 2022-02-16T10:11:34+01:00
weight: 3
---

HiCognition uses collections to group datasets together for them to be available for some of the more complex processing algorithms.

## Collection types

There are two types of collections in HiCognition, which are defined by the types of datasets they contain.

### 1D-feature collections

1D-feature collections are named groups of [1D-features](/docs/data_management/features/#bigwig-files-1d-features), which can be used for preprocessing data for display in the [1D-feature embedding widget](/docs/widgets/1d_feature_embedding/)

### Region collections

Region collections are named groups of [genomic regions](/docs/data_management/regions/), which can be used for preprocessing data for display in the [Association widget](/docs/widgets/association/)

## Creating collections

Creating collections can be done by first clicking the `Create Dataset Collection` button in the data management drawer:

![create collection menu](/docs/create_collection_menu.png)

This causes a dialogue to pop up:

![create collection dialogue](/docs/create_dataset_collection_dialogue.png)

Datasets can be selected via the `Select Datasets` button that causes the [dataset table component](/docs/data_management/regions/#viewing) to appear. There, you can select which datasets your collection should contain. You can then give the collection a name and hit `Submit Collection` to create the collection. 

## Managing collections

To view your collections, you can hit the `Show Dataset Collections` button in the data management drawer:

![show dataset collections menu](/docs/show_dataset_collections_menu.png)

This will cause a dialogue to appear that lets you look at all your dataset collections:

![collection table](/docs/dataset_collection_table.png)

This table is similar to the table that [allows viewing datasets](/docs/data_management/regions/#viewing) except that it does not allow filtering based on descriptions (because collections have no description) and that the number of available fields is much lower. If you want to view which datasets are contained in a collection, you need to click on the number of contained datasets:

![click contained datasets](/docs/click_on_contained_datasets.png)

This will cause a dialogue to pop up that allows you to view the contained datasets:

![contained dataset table](/docs/contained_dataset_table.png)

If you want to delete a collection, select it and then click the `Delete` button.