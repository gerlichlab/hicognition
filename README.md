# HiCognition

Flask server for HiCognition with Vue.js frontend. HiCognition is a a data exploration tool that aims to allow stream-lined exploration of aggregate genomic data. HiCognition is centered around Hi-C data, but also enables integration of Chip-seq and region based data.

## Requirements

HiCognition runs on [docker](https://www.docker.com/) and therefore needs docker to be installed on your system.

## Installation

Clone this repo into a local folder:

```git clone git@github.com:gerlichlab/HiCognition_flask.git```

and you are ready to got!

## Running the app

Open a powershell/bash session and change into the `hicognition_flask` directory.
In that directory, start the docker network with the following command:

```docker-compose up -d```

This will start HiCognition in the background. If this is the first time you are running the app, this will download docker-image dependencies and build the local containers. Once this command has finished, HiCognition is available at `http://localhost/`.

If you need to access log-files, can do so via `docker-compose -logs`

## Project architecture and design decisions

For a detailed description of the project architecture and development design decisions see our [dev-git](https://github.com/gerlichlab/HiCognition_devgit).
