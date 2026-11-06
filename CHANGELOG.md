# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project will adhere to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [v0.8.0] - 2026-11-06
The last release on the original stack (Python 3.8, Flask 1.1, Vue 2), as the lab's instance runs it. [#36](https://github.com/gerlichlab/hicognition/issues/36) moves every dependency to its newest release.

### Added
* **Datasets carry a Sample ID.** The single upload form, the bulk upload and the form that edits a dataset ask for it and require it, and the dataset table shows it as a column. The `sample_id` column already existed in the database, so no migration runs.
* **Anyone can register an account.** The "Create user" button of the registration form was disabled, with the tooltip "Public registration will be available soon!"; it now submits the form, and the new account is activated through the confirmation e-mail.
* **Citation metadata for Zenodo** in `.zenodo.json`, and the Zenodo DOI badge in the README.
* **`mysql/backup_db.sh` dumps the database, meant to run from cron on the docker host.** It writes `hicognition_<date>_<time>.sql.gz` into `MYSQL_BACKUP_DIR`, readable by its owner only, checks that mysqldump completed the dump, copies it to `BACKUP_COPY_DIR` if that is set (the folder must exist, so a share that is not mounted fails the run), and deletes dumps, and the partial files of failed runs, older than `BACKUP_KEEP_DAYS` days (14 unless set). The settings come from the environment or from `.env`. Until now nothing wrote backups: the `MYSQL_BACKUP_DIR` folder was mounted into the MySQL container and stayed empty.

### Changed
* **Pileups and stackups are precomputed for windows of 1, 2, 5, 10 and 20 kb, and at finer bin sizes.** Windows of 1, 2 and 5 kb get BigWig stackups and collection enrichments only, at 100 and 500 bp. Coolers get 1 kb pileups for 10, 20, 50 and 100 kb windows, where 50 and 100 kb had only 5 kb, and 1 kb instead of 2 kb for 50 kb windows of small regions. BigWigs get one finer bin size at every window size from 50 kb up, for example 1 kb at 100 kb and 10 kb at 1 Mb.
* **Cooler pileups for 1 Mb windows are also computed at 25 kb,** for coolers zoomified without a 20 kb resolution.
* **Regions of variable size get cooler pileups at 5% of their size only.** At 1% and 2%, pileups on large coolers exceeded the 10-hour job timeout. BigWig stackups and collections keep 1, 2 and 5%.
* **The long-running containers restart unless they were stopped,** so an instance comes back after a crash or a reboot of the host: the Flask server, nginx, Redis, MySQL and the workers. They had no restart policy. The one-shot `node` and `hugo-builder` containers are unchanged.
* **Docker keeps at most 100 MB of logs per container** (5 files of 20 MB), where each container's logs grew without limit on the host's disk.
* **Pileup jobs use more processes:** 10 instead of 5 for the expected (obs/exp) calculation and 5 instead of 2 for the pileup itself, and `docker-compose.yml` starts 5 long-queue and 5 short-queue workers instead of 3.
* **The production `docker-compose.yml` mounts the backend code from the checkout** (`HICOGNITION_DIR` to `/code`) into the server and worker containers, as the development setup does, so a `git pull` and a restart deploy code changes without rebuilding the image; the image only provides the Python environment. The server also mounts `LOG_DIR` to `/logs`, so its logs survive the container being recreated.
* **The backend image builds from `continuumio/miniconda3:22.11.1`** instead of 4.12.0, which fixed an error installing mamba ([mamba#1728](https://github.com/mamba-org/mamba/issues/1728)).
* **The introduction to the public version on the empty start page is no longer shown.** It is shown only when `process.env.LOCAL_INSTALL` is set, which no frontend build defines: the `LOCAL_INSTALL=1` in `docker-compose.yml` is set on the long-queue workers, not on the build.
* **Jenkins pushes images only for the `production` branch:** `hicognition_backend` and `hicognition_nginx`, no longer for `master` and `production_jenkins`, and the Tower deploy jobs for `jenkins-test` and `production_jenkins` are gone. The Tower deploy jobs for `master` and for tags are still configured, although no `master` image is pushed any more.

### Changed (documentation)
* The upload documentation describes uploads from 4D Nucleome and ENCODE, and the genome assemblies page has an example. The README links to the app at app.hicognition.com. The configuration page lists `REDIS_PASSWORD`, and `REDIS_URL` with the password in it, among the variables to set for a new instance.

### Fixed
* **A pileup of a cooler without balancing weights at the requested resolution finishes with an all-NaN result instead of failing the job,** for regions of a fixed size. Calculating the expected raised `KeyError` ("Balancing weight ... not found") and the ICCF pileup `ValueError` (no `bins/weight` column). Pileups of regions of variable size still fail in that case.
* **A 2D embedding whose UMAP step fails finishes with an all-NaN embedding and clusters instead of failing the job.**

### Security
* **Redis is no longer published on the host, and MySQL and the Flask server only on `127.0.0.1`.** `docker-compose.yml` published all three on every network interface, so anyone who could reach the host could use Redis, which has no password and whose queued jobs the workers unpickle and run, connect to MySQL, and call the API without going through nginx. The containers reach each other on the Docker network as before. For diagnostics, use `docker exec`, or an SSH tunnel to the two localhost ports. Only `docker-compose.yml` changed: `docker_server.yml` and the development and integration-test compose files still publish Redis, MySQL and the Flask server on every interface, and the demo files MySQL and the Flask server.
* **Redis requires a password.** `docker-compose.yml` starts Redis with `REDIS_PASSWORD` from `.env` and does not start without it; `REDIS_URL` must contain the same password. Not publishing Redis is not enough on Docker versions before 28.0, where hosts on the same network segment can route to container addresses. The workers now take the URL from the `RQ_REDIS_URL` variable instead of their command line, which every user of the host can read.

## [v0.7] - 2023-05-26
The version submitted with the final version of the manuscript and run at app.hicognition.com ([release](https://github.com/gerlichlab/hicognition/releases/tag/v0.7)).

## [All previous versions]
Versions before v0.7 were not recorded in a changelog; their history is in the git log.
