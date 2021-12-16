#!/bin/bash
while true; do
    flask db upgrade
    if [ $? -eq 0 ]; then
        break
    fi
    echo Upgrade command failed, retrying in 5 secs...
    sleep 5
done
exec gunicorn --bind 0.0.0.0:5000 --access-logfile - --worker-class gevent hicognition_server:app