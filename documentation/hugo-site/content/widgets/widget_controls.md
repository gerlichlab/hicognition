---
title: "Widget controls"
date: 2022-02-18T12:06:53+01:00
weight: 1
---

Widget collections and widgets have controls that allow resizing, zooming, and selecting hosted datasets. Widget collections always have the same set of controls. In contrast, widgets have additional, context-dependent controls that depend on the type of loaded widgets (see the description of widget types in this section).

## Widget Collection

Widget collections represent genomic region sets and can host a variable number of widgets representing genomic features at this shared region set. Thus, the controls found on widget collections can change the selected region set and the arrangement of contained widgets.

### Select genomic region set

To select a genomic region set, click on the middle button at the top of a given widget collection:

<img src="/docs/Select_region_set_collection.png" class="quarter-width">

This will cause the [dataset selection dialogue](/docs/data_management/regions/#viewing) to pop-up, where you can select a genomic region set for this widget collection:

<img src="/docs/region_dataset_table.png" class="half-width">

Once selected, the name of the selected region set will be displayed on the blue horizontal bar at the top of the widget collection.
<img src="/docs/widget_collection_context_bar.png" class="quarter-width">

### Set window size

If your region set is a point-features (see [this section](/docs/data_management/regions/#types-of-genomic-regions) for a detailed explanation), the top controls of the widget collection will allow you to select the specific window size that all the widgets inside the collection display:

<img src="/docs/window_size_selection.png" class="quarter-width">

This means that with this selection, you can "zoom" in and out of your genomic region of interest to observe effect at different genomic scales.

### Resize and delete widget collection

You can resize the widget collection with all of its containing widgets using the controls at the top-left of the widget collection:

<img src="/docs/widget_collection_context_bar.png" class="quarter-width">

{{% notice note %}}
Note that widget collections have a set minimum size beyond which you cannot shrink the widget collection.
{{% /notice %}}

If you want to delete a widget collection, you can click on the garbage can at the top right.

### Creating slots

Widget collections can contain multiple slots for widgets. These slots can be created by hitting the arrow buttons on the right and bottom of a widget collection. For example, you can click the arrow on the right to create an additional slot for a widget:


<img src="/docs/resize_widget_collection.png" class="half-width">

### Creating widgets

To create a widget, you can hover over the central <img src="/docs/plus_button.png" class="inline-picture"> button inside the widget slot to reveal the widget selection menu:

<img src="/docs/widget_selection_menu.png" class="quarter-width">

Once you click on a specific widget, the slot gets filled with an empty widget of that type:


<img src="/docs/collection_w_one_widget.png" class="quarter-width">

### Arranging widgets

Widgets can be dragged from one slot to another in order to create the perfect arrangements for your analysis question. For this, just drag the widget to your target slot:

<img src="/docs/dragging_widget.png" class="three-quarter-width">


## Widgets

All widget types have their own "widget controls" described in the chapter of the respective widgets. In addition to that, all widgets share controls for selecting datasets, selecting bin size, and deleting widgets.

### Selecting genomic features

To select a genomic feature for a given widget, click the button on the top right.

<img src="/docs/select_dataset_widget.png" class="one-quarter-width">

This will open the [dataset selection table](/docs/data_management/regions/#viewing) or the [collection selection table](/docs/data_management/collections/#managing-collections) depending on which data type is suitable for the current widget. Using this table, you can select which features you want to load into the given widget.

### Changing bin size

To change the genomic resolution at which you want to look at the data, you can select the desired binsize from the binsize dropdown at the top of each widget.

<img src="/docs/changing_binsize.png" class="one-quarter-width">

{{% notice note %}}
For point features, binsize will be in genomic coordinates, whereas for interval features, binsize will be in the percentage of the respective region size. See this [section](/docs/data_management/regions/#types-of-genomic-regions) for a more detailed explanation.
{{% /notice %}}
