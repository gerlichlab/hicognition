#!/bin/bash
wait-on http://hicognition:5000/api/test &&\
wait-on http-get://node:8080/static/serverAlive.json &&\
cypress run