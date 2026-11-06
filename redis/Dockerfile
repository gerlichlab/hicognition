# Valkey, the BSD-licensed fork of Redis 7.2, which the Linux Foundation maintains. HiCognition
# uses it as Redis: rq's queues and the notifications' pub/sub. It reads redis.conf as it is.
FROM valkey/valkey:9.1.3-alpine
COPY redis.conf /usr/local/etc/valkey/valkey.conf
# valkey-server by that name: the image's entrypoint drops root only for it
CMD [ "valkey-server", "/usr/local/etc/valkey/valkey.conf" ]
