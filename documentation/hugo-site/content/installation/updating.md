---
title: "Updating"
date: 2022-02-04T14:07:42+01:00
draft: true
weight: 4
---

Updating HiCognition is relatively easy since all changes to the code can be integrated by rebuilding the containers and since we use automatic database migration tools, all changes to the MySQL database are applied automatically. The only exception to this would be changes that break compatibility with older, cached preprocessing data. But this exceptions will be communicated with the newest release and contain a detailed guide on the migrate old versions to new ones.

### Get the new version

To get the newest HiCognition version (or any version you would like to run), first stop any running HiCognition instance via

```bash
cd HiCognition
docker-compose down
```

where `HiCognition` refers to the location of the cloned HiCognition github repository. Then, get the latest version using git. E.g.

```bash
git fetch --all
git checkout master # or any other branch you would like to use
git pull # assuming this is not a new branch
```

### Rebuild containers

{{% notice note %}}
We are currently in the process of migrating all containers to docker hub. Once this is done, you can then just pull the relevant images from there. Stay tuned!
{{% /notice %}}

In order to integrate all code changes into your local containers, you need to rebuild them via:

```bash
docker-compose build
```

You should expect this process to take 5-10 min.

### Restart HiCognition

After you have downloaded the newest version of HiCognition and rebuilt the containers. You can restart HiCognition using:

```bash
docker-compose up -d
```

This will apply all database migrations to the MySQL database, and start the new versions of all dependent containers. After startup, HiCognition is read to be used!