#!/bin/bash

# check whether showcase raw data is present, if not, downalod and unpack it

if [ ! -d "/showcase_data/raw_data" ]; then
    echo Showcase data not present, downloading...
    cd /showcase_data
    # download and unpack data
    curl -L --silent -o raw_data.tar.gz https://www.dropbox.com/s/6mmmqrwwy1x2dlt/raw_data.tar.gz?dl=0
    tar -xf raw_data.tar.gz
    cd /code
fi

while true; do
    flask db upgrade
    if [ $? -eq 0 ]; then
        break
    fi
    echo Upgrade command failed, retrying in 5 secs...
    sleep 5
done
exec gunicorn --bind 0.0.0.0:5000 --timeout 400 --access-logfile - --worker-class gevent hicognition_server:app
