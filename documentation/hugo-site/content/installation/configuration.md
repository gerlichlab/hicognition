---
title: "Configuration"
date: 2022-02-04T14:06:13+01:00
draft: true
weight: 3
---

The configuration variables are:

- SECRET_KEY - Secret key of flask app that is used to sign the generated token
- SQLALCHMEY_TRACK_MODIFICATIONS - Whether our ORM (SQLAlchemy) should track database modifications
- UPLOAD_DIR - Directory that is used to store uploaded datasets. This filepath is used inside the docker-container and should therefore be in relation to the mounted folder with code and data.
- CHROM_SIZES - Path to the chromosome sizes file on the server filesystem that is needed for the `hicognition` module. This filepath is used inside the docker-container and should therefore be in relation to the mounted folder with code and data.
- CHROM_ARMS - Path to the file harboring genomic locations of chromosomal arms on the server filesystem that is needed for pileups in the `tasks.py` file containing different background tasks. This filepath is used inside the docker-container and should therefore be in relation to the mounted folder with code and data.
- REDIS_URL - URL of redis server
- PREPROCESSING_MAP - Windowsize/binsize combinations that should be precomputed
- BIN_SIZES - Standard bin-sizes that are used for pileups on an uploaded cooler and bed-file
- DEBUG - Whether the flask server should be started in debug mode or not
- TESTING - Flag that indicates whether server is in testing mode or not (Currently unused)
- STACKUP_THRESHOLD - From how many regions on a stackup should be downsampled
- OBS_EXP_PROCESSES - How many processes should be used to compute obs/exp
- PILEUP_PROCESSES - How many processes should be used to construct pileups
- SQLALCHEMY_DATABASE_URI - URL of the database. Note that if only `sqlite://` is specified (as in the `TestingConfig` class, the database is created in memory)