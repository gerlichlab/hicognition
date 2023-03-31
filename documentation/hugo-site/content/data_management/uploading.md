---
title: "Uploading"
date: 2022-02-16T10:11:34+01:00
weight: 3
---

In general, HiCognition allows two different types of uploads:
- either directly from your computer 
- or by providing it via an online location.

{{% notice tip %}}
We highly recommend direct ingestion via online locations with big files; not only do you not need to wait (HiCognition will inform you once the download is finished), but it also avoids time-out errors with very big files.
{{% /notice %}}

## Online repositories
HiCognition can deal with multiple repositories and their unique API interfaces. Hicognition was developed to be extendable with more repositories and special login schemes they provide.
We currently support 4D Nucleome and ENCODE.
In the case of 4D Nucleome, you can directly use the unique ID for a data item, and Hicogntion will be able to fetch it for you directly.


## Generic online sources 
Other locations or web sources can be used to ingest the data directly to HiCognition.
These include any web source that provides a link that can be triggered via the browser.
We currently use this feature to download from Dropbox, Amazon cloud storage buckets or data sources directly linked in papers or homepages.


 