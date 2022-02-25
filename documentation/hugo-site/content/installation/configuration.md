---
title: "Configuration"
date: 2022-02-04T14:06:13+01:00
weight: 3
---

Configuring your HiCognition instance can be done using two approaches:

- For common setup tasks, we defined environment variables that need to be available during the start-up
- For more specific configuration, you can edit the flask configuration files

## Environment variables

### Setting environment variables

The most convenient way of setting your environment variables is using a `.env` file that specifies them as key-value pairs. `docker-compose` will use this file - if it is in the same directory -  and inject the variables during start-up.

{{% notice warning %}}
Never commit a `.env` file for your production server to version control!
{{% /notice %}}

Alternatively, you can inject the environment variables in your deploy pipeline. This is probably the cleanest approach and can be easily done with, for example, [github actions](https://docs.github.com/en/actions).

### Available environment variables

#### Production instance

We expose a wide array of environment variables, some of which you don't need to change, whereas others we highly recommend changing.

##### Redefine for new instance

These environment variables should be redefined if you deploy a new HiCognition instance.

- `SECRET_KEY` | Secret key of flask app that is used to sign the generated token
- `DATABASE_URI` | Connection string to the HiCogntion MySQL database (including username and password)
- `MYQSL_PASSWORD` | Password for MySQL database

##### Take from example `.env` file

These environment variables can likely be taken from our example `.env` file and probably only need changing if you are deploying a custom setup.

- `UPLOAD_DIR` | Directory that is used to store uploaded datasets. This filepath is used inside the Docker container and should therefore be in relation to the mounted folder with code and data.
- `CHROM_SIZES` | Path to the chromosome sizes file on the server filesystem that is needed for the `hicognition` module. This filepath is used inside the Docker container and should therefore be in relation to the mounted folder with code and data. 
- `CHROM_ARMS` | Path to the file harboring genomic locations of chromosomal arms on the server filesystem that is needed for pileups in the `tasks.py` file containing different background tasks. This filepath is used inside the Docker container and should therefore be in relation to the mounted folder with code and data.
- `REDIS_URL` | URL of Redis server
- `DIR_FRONT_END` | Relative path to the front_end files.
- `DIR_STATIC` | Static directory for the Nginx server
- `MYSQL_DATA_DIR` | Relative directory to persist MySQL database to
- `INTEGRATION_TESTS` | Relative path to the integration test directory
- `DOC_PATH` | Relative path to documentation files


#### Development instance

{{% notice tip%}}
If you are thinking about setting up a development instance of HiCognition, be sure to check out the [development section](/docs/development).
{{% /notice %}}

In the development instance, the entire HiCognition backend repository is mounted through into the flask server to facilitate hot-reload. You can specify the location of the repository using the following environment variable:

- `HICOGNITION_DIR` | Location of the backend part of the HiCognition repository.

This variable can be taken from our example `.env` file.

## Flask configuration files

If you need to dive deeper into the configuration of HiCognition, you can edit the config file of the flask app (located at `back_end/app/config.py` relative to the HiCognition repository). This config file defines data classes for different configuration states of HiCognition:

- `Config` | Main config class that defines common configuration settings between all config classes
- `DevelopmentConfig` | Development config file that defines settings for flask in development mode
- `TestingConfig` | Config file for flask unittests
- `End2EndConfig` | Config file for integration tests

{{% notice tip%}}
Be sure to rebuild the HiCognition container after you change this config file!
{{% /notice %}}

### Configuration variables related to server setup

{{% notice warning%}}
Note that some of the configuration variables are initialized from environment variables. So if you change them, be sure that environment variables do not override these changes!
{{% /notice %}}

The following configuration variables are related to how the flask server is set up and are most likely not candidates for tuning since they refer to simple paths, flags are secrets:

- `SECTRET_KEY` | Secret key of flask app that is used to sign the generated token
- `SQLALCHEMY_TRACK_MODIFICATIONS` | Flag that specifies whether database modifications should be tracked
- `UPLOAD_DIR` | Directory that is used to store uploaded datasets. This filepath is used inside the Docker container and should therefore be in relation to the mounted folder with code and data.
- `CHROM_SIZES` | Path to the chromosome sizes file on the server filesystem that is needed for the `hicognition` module. This filepath is used inside the Docker container and should therefore be in relation to the mounted folder with code and data. 
- `CHROM_ARMS` | Path to the file harboring genomic locations of chromosomal arms on the server filesystem that is needed for pileups in the `tasks.py` file containing different background tasks. This filepath is used inside the Docker container and should therefore be in relation to the mounted folder with code and data.
- `REDIS_URL` | URL of Redis server
- `TESTING` | Whether the server is in unittesting mode
- `END2END` | Whether the server is in integration testing mode (this is needed for setup of test users in the database)

### Configuration variables related to preprocessing

These configuration variables determine how preprocessing is performed and, depending on the types of tasks at hand, might be in need of adjustment.

#### `PREPROCESSING_MAP` 

The `PREPROCESSING_MAP` configuration variable defines which types of datasets should be processed with what binsize for a given windowsize. The general structure is the following:


```bash
{
    windowsize: {
        datatype: [
            binsize,
            .
            .
            .
        ],
        .
        .
        .
    },
    .
    .
    .
}
```

The default `PREPROCESSING_MAP` has been chosen to provide a balance between resolution and preprocessing time. If your application requires finer resolution or different binsizes, keep in mind that small binsizes at large windowsizes can cause large loads on your server and adjustments should be made with caution.

#### `VARIABLE_SIZE_EXPANSION_FACTOR`

This floating-point number is used when preprocessing regions that have been added as interval features. It specifies how much the snippets should expand to the left and right as a fraction of the specific region.

```txt
Left Expansion                 Region             Right Expansion
---------------|---------------------------------|---------------
```


#### `PIPELINE_NAMES`

This configuration variable defines the preprocessing pipelines to be used for a given datatype. The structure of these values is:

```bash
{
    datatype: (pipeline_function, pipeline_description),
    .
    .
    .
}
```

The `pipeline_function` refers to a function in the file `back_end/app/tasks.py`.

#### `PIPELINE_QUEUES`

This configuration variable holds a mapping between data types and the queue it should be processed on. Currently, we define three different queues:

- `short`
- `medium`
- `long`

The `short` queues is reserved for small tasks that are not related to preprocessing. The `medium` queue refers to tasks that can be typically completed in less than 30s, and the `long` queue refers to tasks that run longer than 30s. The structure of the mapping is:

```bash
{
    datatype: queue,
    .
    .
    .
}
```

#### `CLUSTER_NUMBER_LARGE` and `CLUSTER_NUMBER_SMALL`

These variables refer to the number of clusters to use when grouping regions in the embedding widgets (the [1d-feature embedding widget](/docs/widgets/1d_feature_embedding/) and [2d-feature embedding widget](/docs/widgets/2d_feature_embedding/)). The variable `CLUSTER_NUMBER_LARGE` is used to define small neighborhoods, and the variable `CLUSTER_NUMBER_SMALL` is used to define large neighborhoods (a large number of clusters means that the neighborhood they represent is smaller).

#### `DATASET_OPTION_MAPPING`

This configuration variable defines metadata options for different data types. The general structure is:

```bash
{
        "DatasetType": {
            "bedfile": {
                "ValueType": {
                    "ValueType1": {
                        "Option1": ["Possible", "Values"],
                        .
                        .
                        .
                    },
                    .
                    .
                    .
                }
            },
            "bigwig": {
                "ValueType": {
                    "ValueType1": {
                        "Option1": ["Possible", "Values"],
                        .
                        .
                        .
                    },
                    .
                    .
                    .
                }
            },
            "cooler": {
                "ValueType": {
                    "ValueType1": {
                        "Option1": ["Possible", "Values"],
                        .
                        .
                        .
                    },
                    .
                    .
                    .
                }
            },
        }
    }
```

Here, each dataset type can define multiple value types that can have multiple custom options. Note that changing option values only requires changing this configuration option, whereas adding value types and types of options requires changing the `Dataset` database model.

#### `STACKUP_THRESHOLD`

This configuration variable defines the number of rows above which intervals are downsampled for displaying in the [stacked lineprofile widget](/docs/widgets/stackup/).

#### `OBS_EXP_PROCESSES` and `PILEUP_PROCESSES`

Defines the number of processes to use per worker to calculate observed/expected matrices and pileups, respectively.

## Docker compose files

There are three different Docker compose files that allow starting HiCognition in different modes:

- `docker-compose.yml` | This file is used to start HiCognition in "production mode"
- `docker_dev.yml` | This file is used to start HiCognition in "development mode"
- `docker_integration_tests.yml` | This file is used to run the integration tests (see the [testing section](/docs/development/tests/) for more details)