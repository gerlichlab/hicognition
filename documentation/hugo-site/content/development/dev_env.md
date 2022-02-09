---
title: "Development environment"
date: 2022-02-08T17:40:50+01:00
draft: false
weight: 2
tags: ["development"]
---

## Starting HiCognition in development mode

We provide a docker-compose file that sets up the local development environment. This file uses the same containers as the production compose file, so if you haven't done so, follow the instructions for [building the containers](/docs/installation/build).

When you start a development HiCognition instance, the front-end files will be served by a node.js development server with enabled hot reload. You can then also use the [Vue.js devtools chrome extension](https://chrome.google.com/webstore/detail/vuejs-devtools/nhdogjmejiglipccpnnnanhbledajbpd?hl=en) for debugging. The back-end server that is started in the development instance is a flask development server, also with hot reload.

To get information about how to configure the environment variables for the development instance, see the [configuration](/docs/installation/configuration) chapter.

{{% notice note %}}
The production HiCognition container copies the server code into the container during the build process and runs the server from there. In contrast, the development setup mounts the local code repository into the container to enable fast editing and hot-reload.
{{% /notice %}}

You can start the development instance with the following command inside the cloned HiCognition repository:

```sh
docker-compose -f docker_dev.yml up
```

After that, the app is available on ```http://localhost:8080```

## Get shell access to the server

To get access to the HiCognition flask sever to run tests or interact with the MySQL database through our database models, attach a shell to the `flask-server` container. This can be done with following command:


```bash
docker exec -it flask-server bash
```

Once you have the shell inside the container, you have access to the command line convenience methods that allow quick interactions with the database. You can for example get a python shell with the database models loaded using

```bash
flask shell
```

Additionally, you can add new users using the `flask user define` subcommand:


> __Usage: flask user define [OPTIONS] NAME__
> 
> Creates a new user either with defined password or password prompt. If
> user with the name exists already, password is redefined.
> 
> __Options:__
>
> -p, --password TEXT
>
> --help Show this message and exit.

An example workflow for creating a dummy user with an _unsafe_ password is:


```bash
docker exec -it flask-server bash
flask user define dummy -p 1234
```

To add datasets you can use the `flask dataset add` command:


>  __Usage: flask dataset add [OPTIONS] JSON_PATH USER PASSWORD__
>
>  Adds datasets defined in a JSON to database and uploads it.
>
> __Options:__
>
>  --help  Show this message and exit.

{{% notice note %}}
For bulk upload of data you can also use our [hicognition cli tool](todo)! __TODO__
{{% /notice %}}
