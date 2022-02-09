---
title: "Tests"
date: 2022-02-08T18:24:38+01:00
draft: true
tags: ["development"]
weight: 3
---

All contributions to HiCognition must pass all existing tests and ideally implement new test-cases that test all aspects of new features. The tests are stratified into test for the the flask server ([Backend test](/docs/development/tests/#backend-tests)), tests for the front-end ([Frontend tests](/docs/development/tests/#frontend-tests)) and integration tests that test typical user flows ([Integration tests](/docs/development/tests/#integration-tests)).

## Backend tests

The backend tests test both the request handling of the flask server as well as the preprocessing tasks that run inside the queue worker instances. All example data has been restricted to be very compact such that the tests typically run within ~1 min. If you contribute new tests, we would ask you to abide by the same principle and not use full-length test data.

### Structure

The tests are located in the `back_end\tests` directory relative to the HiCognition repository. The are further structured into the following categories that reside in individual directories:

- __Database models__ | Test the convenience methods of database model classes
- __Delete routes__ | Test flask server delete routes
- __Get routes__ | Test flask server get routes
- __HiCognition package__ | Tests for the hicognition submodule that contains common helper functions
- __Post routes__ | Test flask server post routes
- __Tasks__ | Test preprocessing tasks
- __Testfiles__ | Examples needed to run the tests

Within these directories the tests are distributed to different python files that use the `unittest` framework to setup test-cases and run them. Many of the tests need asses to a test instance of the flask app. This functionality is provided by the `LoginTestCase` class that can be imported from `hicognition.test_helpers`. If tests inherit from this class, each call to `setUp` will create a fresh flask app instance with an in-memory sqlite database. Be sure to call `super().setUp()` if you want to add other setup steps! The `hicognition.test_helpers` file also contains a `TempDirTestCase` class that can be mixed into a testcase to create a temporary directory (accessible via `Te) before the test-suite and clean it up after the suite ash run.


### Running the tests

If you want to run the tests, you need a running development HiCognition instance (see the [guide](/docs/development/dev_env) to find out how you can set this up). Then, you need to attach a shell to the `flask-server` container:

```bash
docker exec -it flask-server bash
```

You can then run the entire backend suite using pytest:


```bash
cd /code
pytest .
```
Alternatively, you can run a specific test file using python (all test files have a unittest entrypoint defined):

```bash
python tests/get_routes/test_api_auth.py
```

{{% notice note %}}
If you change any code inside the `hicognition` package during development, you either need to rebuild the container or install the package in the running container using `pip install .`
{{% /notice %}}


## Frontend tests

The frontend tests test common utility functions that are used throughout the vue.js app.

### Structure

The tests are written using `jest` and are located in `front_end\src\tests` relative to the HiCognition repository.


### Running the tests

If you want to run the tests, you need a running development HiCognition instance (see the [guide](/docs/development/dev_env) to find out how you can set this up). Then, you need to attach a shell to the `node` container:


```bash
docker exec -it node bash
```

You can then run the entire frontend test suite using `npm`:


```bash
cd /front_end
npm run test
```

## Integration tests

The integration tests test common user flows on a running test instance of HiCognition using [cypress](https://www.cypress.io/).

### Structure

The tests are located in `front_end\e2e` relative to the HiCognition repository. This directory contains both the definitions of the tests as well as a `Dockerfile` that defines the cypress docker image to use. The main reason we have a separate image for this is that we include a custom test initialization script (`init.sh`) that defines how to wait on resources needed for running the test (in this cause the flask server startup and finishing the front-end build).

### Running the tests

To run the tests, we provide an integration docker-compose file called `docker_integration_tests.yml` that starts the flask server in `end2end` mode and runs the integration tests. `End2end` mode means that a volatile MySql database is used (no data is persisted outside the MySql docker container) and a test-user is created at app start-up. In addition, the integration test docker-compose file has a slightly different way of building the front-end files such that the file `/dist/static/finished.json` is deposited into the static directory after the build is finished. This file is used by the `init.sh` script of the cypress container to determine that the front-end build has finished.

You can run the integration tests as follows:

```bash
docker-compose -f docker_integration_tests.yml up
```
