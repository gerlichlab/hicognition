---
title: "Build"
date: 2022-02-04T14:06:58+01:00
weight: 2
---

## Clone repository

To get started, first clone the [HiCognition GitHub repository](https://github.com/gerlichlab/HiCognition):

```
git clone --recurse-submodules https://github.com/gerlichlab/HiCognition
```
or 

```
git clone https://github.com/gerlichlab/HiCognition
git submodule init && git submodule update
```
the submodule is needed for the documentary template.

## Build docker images

HiCognition consists of multiple docker images that work together to power the app. The needed images are specified in the `docker-compose.yml` configuration file contained in the Github repository. Once you have cloned the repository, you can build the required images as follows:

```
cd HiCognition # The location that has the cloned GitHub repository
docker-compose build
```

This step will pull multiple large base images and start the build process for HiCognition custom images. This step is expected to take roughly 20 minutes.

## Start HiCognition

After the build process is finished, you can start up a HiCognition instance using the following command:

```
cd HiCognition # The location that has the cloned GitHub repository
docker-compose up -d
```
The `-d` flag specifies that docker-compose should run in the background. The docker-compose configuration starts all components and builds the files for the front-end part of HiCognition. This is expected to take roughly 1 minute. After that, HiCognition is available on port 80 on your local machine!

Thus typing `localhost` into the browser should show you the app.

For the user registration to work, the app must be connected to a mail server to send confirmation links.
To  quickly create an account locally, type into a terminal while hicognition is already running:
```
docker exec -it flask-server bash
flask user define dummy -p 1234
```
This will create the user `dummy` with the password `1234`.

{{% notice warning %}}
The HiCognition repository contains an example environment file that specifies all the needed environment variables. You must change these to ensure that you use non-public passwords and secrets! See the [configuration](/installation/configuration) section for details. 
{{% /notice %}}