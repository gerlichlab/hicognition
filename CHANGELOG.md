# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project will adhere to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
* **Reference results of every preprocessing step, and a test that compares a new run with them by value** ([#36](https://github.com/gerlichlab/hicognition/issues/36)). A small synthetic genome in `back_end/tests/testfiles/reference/` goes through the BED pipeline and every pileup, stackup, enrichment and embedding step, at v0.8.0's window and bin sizes. It has two coolers, three BigWigs and six region files, written by `tests/reference/make_inputs.py`. The results that the lab instance's v0.8.0 image computed are stored beside it, with the versions of the libraries. `tests/reference/test_reference.py` runs the steps again and compares, which takes about 5 minutes. The reference includes what today's code gets wrong, such as the BEDPE pileups that fail ([#38](https://github.com/gerlichlab/hicognition/issues/38)), so a fix shows up as a difference to explain.

### Changed
* **ruff lints and formats the backend in place of black, pylama and pylint, and CI runs on every push to master and every pull request** (ruff 0.17.3, as in looptrace): the lint, the backend tests with the reference comparison in an image built from the lock, and the frontend tests. Before, every workflow ran only when started by hand, and the backend tests pulled an image with the version in `back_end/VERSION`, which Docker Hub doesn't have. pre-commit runs ruff on every commit.
* **The pileup, expected and LOLA code of `ngs` and `pylola` is part of HiCognition now,** in `back_end/app/lib/` (`hic_tools.py`, `snipping.py`, `lola.py`), with their tests and their MIT notices ([#36](https://github.com/gerlichlab/hicognition/issues/36)). It moved unchanged, apart from formatting. The backend image no longer installs `ngs` v0.3b, `pylola` or `hicognition_lib` from GitHub. Nothing imported `hicognition_lib`. The functions of `ngs` that HiCognition doesn't call stayed behind, and with them its only use of `pairtools`. The versions they pinned (cooltools 0.4.0, bioframe 0.2.0, pandas 1.2.4, scipy 1.5.2) held the whole backend back; the code now runs on cooltools 0.7, bioframe 0.8 and pandas 2.3.
* **The backend runs on Python 3.13, with every dependency at its newest release, from a Poetry lock** ([#36](https://github.com/gerlichlab/hicognition/issues/36)). The image is `python:3.13-slim-trixie` with `back_end/pyproject.toml` and `back_end/poetry.lock`, in place of conda on Python 3.8, whose environment could no longer be built. Among the moves: numpy 1.23 → 2.5, pandas 1.2 → 2.3, cooltools 0.4 → 0.7, bioframe 0.2 → 0.8, cooler 0.8 → 0.12, scikit-learn 1.1 → 1.9, umap-learn 0.5.3 → 0.5.12, Flask 1.1 → 3.1, SQLAlchemy 1.3 → 2.1, pydantic 1 → 2, rq 1.8 → 3.0, redis-py 3.5 → 8.1, gunicorn 20 → 26 and gevent 21 → 26. Two pins have their reasons beside them in `pyproject.toml`: Python 3.13, since pybbi has no wheels for 3.14, and pandas 2.3, since cooltools 0.7.1 indexes Series by position, which pandas 3 refuses.
* **Some results move with the new libraries;** the reference results show where. Fixed-size pileups, ICCF and Obs/Exp, and the LOLA enrichments are otherwise identical to v0.8.0's.
  * **Embeddings and their clusters, 1D and 2D, come out differently:** umap-learn 0.5.12 lays out the same input differently from 0.5.3, with the same seed. KMeans keeps its 10 initialisations, which scikit-learn's default no longer is.
  * **A stackup bin that reaches past the end of a chromosome is NaN** (pybbi 0.4), where it held the mean of its part inside the chromosome.
  * **Obs/Exp pileups of variable-size regions differ in a few pixels near the diagonal:** scikit-image 0.26 spreads NaN slightly further when it resizes the windows. In the reference results that is at most 2.4% in 3% of a pileup's pixels.
  * **The expected of an arm that ends inside a bin is slightly lower:** cooltools 0.7 leaves the pixels touching that bin out of the balanced sum, but not out of the count of valid pixels. With hg19's arms that happens only at 20 kb, for 9 short arms, by 0.02–0.05%. `count.sum`, which HiCognition doesn't use, now leaves out bins without balancing weights.
  * The reference results are now those of the new libraries; v0.8.0's are in the commit that added them.
* **Login and session tokens keep their format,** although itsdangerous 2.1 removed the serializers that wrote them (`app/lib/tokens.py`). Links to shared sessions keep working, and nobody is logged out.
* **Valkey 9.1 replaces Redis 6 for rq's queues and the notifications** ([#36](https://github.com/gerlichlab/hicognition/issues/36)). Valkey is the BSD-licensed fork of Redis 7.2, maintained under the Linux Foundation; Redis itself left the BSD license with 7.4. It reads `redis/redis.conf` unchanged, apart from the pid file, which the server, running in the foreground as the unprivileged `valkey` user, needs no more. The service keeps its name `redis-server`, so `REDIS_URL` and `REDIS_PASSWORD` stay as they are.
* **New passwords are hashed with PBKDF2-SHA256 at 1,000,000 iterations,** Werkzeug 3's setting for it. Werkzeug 3's default, scrypt, writes hashes longer than the database column; existing hashes still verify.

### Changed (documentation)
* The developer documentation names ruff and pre-commit in place of black, pylama and pyright, Valkey in place of Redis 6, and the testing page the reference results.

### Removed
* **conda, and the packages nothing imported** ([#36](https://github.com/gerlichlab/hicognition/issues/36)): matplotlib, seaborn, statsmodels, pairtools, pybedtools, pysam, pyensembl, pyarrow, flask-cors, pyhumps, PyJWT, the Flask-Babel, Flask-Bootstrap, Flask-Moment and Flask-WTF extensions, black, pylama and pylint. The image no longer installs anything from GitHub.

### Fixed
* **A new database can be built again.** One migration passed `type` to `drop_constraint`, which Alembic 1.20 refuses; it is `type_`.
* **The default paths of the chromosome sizes and arms, the upload folder and the development databases point into `back_end/` again.** Since the configuration file moved into `back_end/app/config/`, they pointed there, where none of these files are. It went unnoticed because deployments set the paths in `.env`, but the backend tests failed without them.

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
