# HiCognition: A visual exploration and hypothesis testing tool for 3D genomics

[![Python code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black "Black: The Uncompromising Code Formatter")
[![Javascript Style Guide: Prettier](https://img.shields.io/badge/code_style-prettier-ff69b4.svg?style=flat-square)](https://github.com/prettier/prettier-vscode "Prettier: An Opinionated Code Formatter")
![Build and push image](https://github.com/gerlichlab/HiCognition/actions/workflows/build_and_push_image.yml/badge.svg)
![Run backend tests](https://github.com/gerlichlab/HiCognition/actions/workflows/run-backend-tests.yml/badge.svg)
![Run front-end tests](https://github.com/gerlichlab/HiCognition/actions/workflows/run-front-end-tests.yml/badge.svg)
![Run integration tests](https://github.com/gerlichlab/HiCognition/actions/workflows/run-integration-tests.yml/badge.svg)

<img src="documentation/logo.svg" width="500px">

HiCognition is a data exploration tool that allows stream-lined exploration of aggregate genomic data. HiCognition is centered around Hi-C data but also enables integration of Chip-seq and region-based data.

HiCognition implements the region-set focus approach, a concept that allows exploration of genomic region sets. For more details see the [concepts section](https://hicognition.com/docs/concepts/) of our documentation.

## Get started

To get started using HiCognition, check out the [quickstart section](https://hicognition.com/docs/getting_started/get_started_w_example_data/) of our documentation.


## Installation

If you want to set-up a HiCognition instance yourself, check out the [installation section](https://hicognition.com/docs/installation/) of our documentation. An optional CLI tool to interface with the web API can be found in the [HiCognition library](https://github.com/gerlichlab/hicognition_lib) repository is under development.

## Development

If you want to contribute to HiCognition, be sure to read the [development section](https://hicognition.com/docs/development/) or our documentation.

## Citing

Langer, C. C. H.<sup>\*</sup>, Mitter, M.<sup>\*</sup>, Stocsits, R. R. & Gerlich, D. W. (2022) HiCognition: a visual exploration and hypothesis testing tool for 3D genomics. _bioRxiv_ doi:[10.1101/2022.04.30.490134](https://www.biorxiv.org/content/early/2022/05/01/2022.04.30.490134)

<sup>\*</sup> equal contribution

```bibtex
@article {HiCognition2022,
	author = {Langer, Christoph C. H. and Mitter, Michael and Stocsits, Roman R. and Gerlich, Daniel W.},
	title = {HiCognition: a visual exploration and hypothesis testing tool for 3D genomics},
	year = {2022},
	doi = {10.1101/2022.04.30.490134},
	URL = {https://www.biorxiv.org/content/early/2022/05/01/2022.04.30.490134},
	journal = {bioRxiv}
}
```


If you want to contribute to HiCognition, be sure to read the [development section](https://gerlichlab.github.io/hicognition/docs/development/) or our documentation.

## Public server

A demo version with all of the sessions used for the figures of the manuscript can be found on our [homepage](https://app.hicognition.com/). The server has all functionality enabled and users can sign up for a free account using a valid e-mail address to gain fast hands-on experience of HiCognition.
