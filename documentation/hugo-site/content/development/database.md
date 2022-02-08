---
title: "Database"
date: 2022-02-08T18:25:46+01:00
draft: true
---

The flask-server and the redis-queue worker use a common database to record and change information about users and datasets. We use [SQLAlchemy](https://www.sqlalchemy.org/) as an Object-relational-mapper (ORM) to abstract details of the underlying database. This allows in principle to quickly change database back-ends and allows interaction with the database via python classes and functions. Currently, we use MySQL to store meta-information about datasets (file-path, name, etc.) and users directly in the database and large data (images, raw-files, processed-files...) is stored on the filesystem.

Database migrations are managed using [FLASK-Migrate](https://flask-migrate.readthedocs.io/en/latest/) that is a wrapper for [alembic](https://alembic.sqlalchemy.org/en/latest/), a database migration tool for SQLAlchemy. Using this set-up, database migrations are scheduled using 'flask db migrate -m $MESSAGE', which creates a migration script in the `./migrations` sub-folder. This migration can then be applied using `flask db upgrade`. The `./migrations` directory is committed to version control and records the migration-history of our database. The development workflow is to define database models in a `models.py` file and commit a migration to version control. Then, on the production server, the newest changes - including the migration script - are pulled and the database migrated to the newest version using `flask db upgrade`.

Interactions with the database are managed by [FLASK-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/), which uses a `ScopedSession` object as `db` throughout the app, that ensures thread-safety of database interactions.

## Database model

Details are [here](https://github.com/gerlichlab/HiCognition_flask/blob/master/app/models.py), this is an overview drawn using https://dbdiagram.io/home:

![DB-model](/docs/Hicognition_db.png)


The tables are used to store the following information:

- User - Information about the user including which datasets and tasks the user owns
- Dataset - Information about datasets (bed-files or cooler-files) with their higlass-uuid (the id in the higlass-internal sqlite database), the file-path of this dataset as well as back-refs to the owning user an refs to the pileupregions, pileups and tasks that are associated with a given dataset.
- Pileupregion - Regions derived from a bed-file Dataset that spans +/- windowsize up- and downstream. Contains a file-path to a bedpe-file holding these records and a higlass-uuid that refers to the id of the bedpe file in the higlass-internal database.
- Pileup - Pileup derived using a cooler dataset and a pileupregion. Contains the file_path to the json-file holding the pileup-information, the binsize that was used for the pileup, the value_type - which is either raw counts or obs/exp values -  as well as back-refs for the cooler_id and pileupregion_id used for the pileup
- Task - A background task in the redis-queue that contains as id the id of the job in the redis server, back-refs to the user_id that submitted the task as well as the dataset_id that is being processed. Also contains a complete flag that indicates whether the job is complete.



## Changing Database

```
docker exec -it flask-server bash
```
Then

```
cd /code
flask db migrate -m "COMMIT-NAME"
flask db upgrade
```
