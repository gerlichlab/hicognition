# HiCognition

[![Python code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black "Black: The Uncompromising Code Formatter")
[![Javascript Style Guide: Prettier](https://img.shields.io/badge/code_style-prettier-ff69b4.svg?style=flat-square)](https://github.com/prettier/prettier-vscode "Prettier: An Opinionated Code Formatter")

[TODO:]:<> ( Add: docs badge, build badge, coverage badge. More on: https://github.com/dwyl/repo-badges)

Flask server for HiCognition with Vue.js frontend. HiCognition is a a data exploration tool that aims to allow stream-lined exploration of aggregate genomic data. HiCognition is centered around Hi-C data, but also enables integration of Chip-seq and region based data.

## Requirements

HiCognition runs on [docker](https://www.docker.com/) and therefore needs docker to be installed on your system.

## Development
Start vom development server:
```
docker-compose -f docker_dev.yml up
```
if you get a network error:
```
docker-compose -f docker_dev.yml down
```

To create a user,
attach a shell to ```flask-dev``` container with
```
docker exec -it flask-dev bash
```
Then

```
source activate flask
cd /code
```

Then type

```
flask shell
``` 

to start python in the app context, and then enter:

``` 
new_user = User(username="dummy")
new_user.set_password("1234")
db.session.add(new_user)
db.session.commit()
```

view the app on ```http://localhost:8080```

## Running tests

```
docker exec -it flask-dev bash
```
Then

```
source activate flask
cd /code
pytest .
```
The /code folder is linked to the outside of the container in your git folder.
Attention, if you test changes run first:
```
pip install .
```

## Changing Database

```
docker exec -it flask-dev bash
```
Then

```
source activate flask
cd /code
flask db migrate -m "rename fields"
flask db upgrade
```


## Installation

Clone this repo into a local folder:

```
git clone https://github.com/gerlichlab/HiCognition_flask
```

and you are ready to got!

## Running the app

Open a powershell/bash session and change into the `hicognition_flask` directory.
In that directory, start the docker network with the following command:

```
docker-compose up -d
```

This will start HiCognition in the background. If this is the first time you are running the app, this will download docker-image dependencies and build the local containers. Once this command has finished, HiCognition is available at `http://localhost/`

If you need to access log-files, can do so via 
```
docker-compose -logs
```
execute the command above in the root directory of this repo.

## Project architecture and design decisions

For a detailed description of the project architecture and development design decisions see our [dev-git](https://github.com/gerlichlab/HiCognition_devgit).

## Fullsize test data
A .mcool, .bw and .bed file can be found ar this [dropbox](https://www.dropbox.com/sh/zjfc6sgkbdp3ksh/AAAWrbgKt8hz4npNxSfh-RBja?dl=0) location.
