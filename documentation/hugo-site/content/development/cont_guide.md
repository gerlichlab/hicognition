---
title: "Contribution guide"
date: 2022-02-09T13:44:15+01:00
draft: false
weight: 5
tags: ["development"]
---

HiCognition is an open source project and as such we welcome all contributions to our code base. The main requirement for a contribution to be accepted is that it passes all test (described in detail [here](/docs/development/tests)) and conforms to our style decisions. 

## Automatic testing

When a pull request is issued on the HiCognition github repository, we have set up git actions that check the code for linting issues, run it against or formatting guidelines and dispatch our testing suite. This means that in principle you don't need to setup local testing, although we highly recommend doing so to decrease frustration (see our [testing guide](/docs/development/tests) to learn how to set up local testing.).


## Formatting guidelines

We use [black](https://github.com/psf/black) for code formatting to have a consistent way our python code looks. The automatic actions will run

```bash
black --check .
```
against your code, so we recommend to use black for python code formatting beforehand.

## Linting

We use pylint to check code for linting issues using the following command:

```bash
pylint --disable=C0330 --fail-under=8 app/
```

## Documentation guidelines

Every function/class should have docstrings according to the rules laid out in [PEP257](https://www.python.org/dev/peps/pep-0257/):

>Multi-line docstrings consist of a summary line just like a one-line docstring, followed by a blank line, followed by a more elaborate description. The summary line may be used by automatic indexing tools; it is important that it fits on one line and is separated from the rest of the docstring by a blank line. The summary line may be on the same line as the opening quotes or on the next line. The entire docstring is indented the same as the quotes at its first line (see example below).