---
title: "Manage preprocessing"
date: 2022-02-17T10:29:35+01:00
weight: 2
---

HiCognition provides a user interface to submit preprocessing tasks and check their progress.


## Submit tasks

Depending on whether you want to submit a task for features or collections (see [here](/preprocessing/job_types/) for more details), click either `Preprocess Features` or `Preprocess Collections` in the data management drawer:

<img src="/preprocess_menu.png" class="quarter-width">


This will open the preprocessing dialogue:

<img src="/preprocess_dialogue.png" class="three-quarter-width">



Here, you first need to select for which region you want to start preprocessing. To do this, click on the `Select region` button. This will open up the [dataset management table](/data_management/regions/#viewing) and allow you to select a genomic region:


<img src="/select_dataset_preprocessing.png" class="three-quarter-width">


Once you select the region, the `Select Features`/`Select Collections` button becomes available. If you click on it, this will again open either the dataset management table or the [collection management table](/data_management/collections/#managing-collections). Here, you can then select which features/collections should be preprocessed. Once you hit `Select`, the dialogue disappears, and you can hit the `Submit Job` button, which will cause preprocessing to be started.

<img src="/preprocessing_both_things_selected.png" class="three-quarter-width">


{{% notice note %}}
Currently, there is a one-to-one mapping between preprocessing tasks and types of datasets. E.g., there is only one possible task for a 2D feature. Therefore, the preprocessing dialogue does not require the selection of the task type. In the future, this might change, and the dialogue will become more complex.
{{% /notice %}}

## Check tasks

Once your tasks are running, you can check their progress via the [dataset management table](/data_management/regions/#viewing). If you open up the table, you can see two fields that are called `Processing Features` and `Processing Collections`. These indicate at a glance how many genomic features and feature collections are being processed for a given genomic region set. If you click on the columns, you can sort the table by this field and quickly see which datasets are processing:

<img src="/processing_datasets_table.png" class="three-quarter-width">


If you want more information about task progress and also view which features and collections are available for a given genomic region set, you can click on the processing feature number and inspect the pop-up dialogue:

<img src="/processing_status_table.png" class="three-quarter-width">

This table shows an additional status column that indicates whether a feature is currently processing, is already available, or has not been processed yet:



| Icon | Meaning  |
|-------------|-------------------------------------------------------------|
| <img src="/progress_spinner.png" style="margin: auto">       | This icon means that this particular feature is currently processing                    |
| <img src="/tick.png"  style="margin: auto">       | This icon means that this particular feature has finished processing and is available |
| <img src="/upload_cload.png"  style="margin: auto">      | This icon means that the feature has been uploaded and is available, but has not been preprocessed                            |

## Notifications

When your preprocessing jobs finish, you will receive notifications. These are visible at the right side of the top toolbar:

<img src="/notification_icon.png" class="half-width">

If you click on the notification symbol, a side-drawer opens, where you can see that features finished preprocessing for which genomic region set:

<img src=/notification_drawer.png class="half-width">

If you click on the envelope symbol, you can acknowledge the notifications and mark them as read.


{{% notice note %}}
We don't persist notifications in the database, so notifications are only visible in one viewing session. So, if you reload the browser or log out, the notifications will not be visible anymore.
{{% /notice %}}