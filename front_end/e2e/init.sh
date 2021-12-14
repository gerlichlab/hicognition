#!/bin/bash
wait-on --interval 1000 http://hicognition:5000/api/test &&\
wait-on --interval 1000 http://nginx/static/finished.json &&\
cypress run