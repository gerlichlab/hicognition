+++
title = "Preprocessing"
date = 2022-02-03T15:34:57+01:00
weight = 5
chapter = true
pre = "<b>5. </b>"
+++

# Preprocessing

HiCognition is a visual exploration tool that allows users to explore the aggregate behavior of genomic features (see the [concepts section](/concepts) for more detail). This means that this aggregate behavior needs to be computed for a given genomic region and genomic feature combination. Therefore, HiCognition provides both a job queue that runs the preprocessing (see the [architecture section](/development/development_info/) for more details on this) and a user interface to submit jobs and check their status. 

## [Preprocessing tasks](/preprocessing/job_types/)
The section described the different types of preprocessing steps HiCognition performs in the background to explore the genomic data via the widgets in real-time.
 
## [Manage preprocessing](/preprocessing/manage_preprocessing/)
This chapter describes the user interface to submit preprocessing tasks and check their progress.