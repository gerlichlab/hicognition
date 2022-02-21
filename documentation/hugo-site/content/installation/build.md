---
title: "Build"
date: 2022-02-04T14:06:58+01:00
weight: 2
---

## Clone respository

To get started, first clone the [HiCognition github repository](https://github.com/gerlichlab/HiCognition):

```
git clone https://github.com/gerlichlab/HiCognition
```

## Build docker images

HiCognition consists of multiple docker images that work together to power the app. The needed images are specified in the `docker-compose.yml` configuration file contained in the github repository. Once you cloned the repository, you can build the required images as follows:

```
cd HiCognition # The location that has the cloned github repository
docker-compose build
```

This step will pull multiple large base images and start the build process for HiCognition custom images. This step is expected to take roughly 20 minutes.

## Start HiCognition

After the build process is finished, you can start up a HiCognition instance using the following command:

```
cd HiCognition # The location that has the cloned github repository
docker-compose up -d
```

The `-d` flag specifies that docker-compose should run in the background. The docker-compose configuration starts all components and builds the files for the front-end part of HiCognition. This is expected to take roughly 1 minute. After that, HiCognition is available on port 80 on your local machine!

{{% notice warning %}}
The HiCognition repository contains an example environment file that specifies all the needed environment variables. It is very important that you change these
to ensure that your are using non-public passwords and secrets! See the [configuration](/docs/installation/configuration) section for details. 
{{% /notice %}}