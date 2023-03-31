+++
title = "Preprocessing"
date = 2022-02-03T15:34:57+01:00
weight = 5
chapter = true
pre = "<b>5. </b>"
+++

# Preprocessing

HiCognition is a visual exploration tool allowing assessment of aggregate behavior of genomic features (see the [concepts section](/concepts) for more detail).
This means that for a given combination of regions and features these aggregate behaviours need to be computed beforehand.
HiCognition provides a job queue that runs the preprocessing (see the [architecture section](/development/development_info/) for more details on this) and a user interface to submit jobs and check their status. 

## [Preprocessing tasks](/preprocessing/job_types/)
This section describes the different types of preprocessings, performed in the background, for different region/feature-combinations. 
The resulting data is used for exploration via the plotting widgets in real-time.
 
## [Manage preprocessing](/preprocessing/manage_preprocessing/)
This chapter explains how start preprocessing tasks and check their progress.


<!-- 
Note Ulrich:
Do you think this part is necesary?
For the user the different preprocessing steps are not perceivable, they just click "Preprocess".

>