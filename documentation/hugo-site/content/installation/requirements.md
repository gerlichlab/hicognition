---
title: "Requirements"
date: 2022-02-04T14:04:22+01:00
weight: 1
---

## Software

The only software requirement for HiCognition is `docker`. To install Docker, follow the respective [installation guide for your platform](https://docs.docker.com/get-docker/). All needed containers are specified in the docker-compose file in the HiCognition repository (see [build](/installation/build) for more details).

## Hardware

HiCognition is an integrated data exploration and preprocessing platform. This means that it is not only responsible for displaying visualizations but also provides a preprocessing queue (see [preprocessing](/preprocessing) for more details) to calculate aggregation data of large genomic data sets. Thus, the server running HiCognition needs to be sufficiently powerful to allow these preprocessing steps. While the number of parallel worker processes for preprocessing and the maximum genomic resolution can be specified in the server configuration (see [configuration](/installation/configuration) for more details), we recommend using a server with the following minimum specifications:

| Number of simultaneous users | CPU      | Memory | Disk space |
|------------------------------|----------|--------|------------|
| 5                            | 4 cores  | 8 Gb   | 100 Gb     |
| 10                           | 16 cores | 32 Gb  | 200 Gb     |
| 20                           | 32 cores | 64 Gb  | 400 Gb     |

It is somewhat difficult to estimate how to derive the number of simultaneous users from the total numbers of users. Therefore, we recommend monitoring resource usage closely when initially setting up HiCognition.