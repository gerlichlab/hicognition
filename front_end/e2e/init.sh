#!/bin/bash
wait-on http://hicognition:5000/api/test &&\
wait-on http://nginx/static/finished.json &&\
cypress run