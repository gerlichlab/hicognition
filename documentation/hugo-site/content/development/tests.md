---
title: "Tests"
date: 2022-02-08T18:24:38+01:00
draft: true
tags: ["development"]
---

## Tests

### Running tests backend

```
docker exec -it flask-server bash
```
Then

```
cd /code
pytest .
```
The /code folder is linked to the outside of the container in your git folder.
Attention, if you test changes run first:
```
pip install .
```

### Running tests frontend
```
docker exec -it node bash
```
Then

```
cd /front_end
npm run test
```