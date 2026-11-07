# Resolve learn submodule
FROM ubuntu:24.04 AS theme-resolver

# Install git

RUN apt-get update -y &&\
    apt-get install -y git

ADD . /code

# resolve learn submodule

RUN cd /code && git submodule update --init --recursive

# build documentation
FROM klakegg/hugo as hugo-builder

# copy files into container

COPY --from=theme-resolver /code/documentation/hugo-site/ /docs/


# build hugo

RUN cd /docs/ && hugo

# build frontend
FROM node:24.22.2-trixie-slim AS frontend-builder

ADD ./front_end /front_end

RUN cd /front_end && npm ci --no-audit --no-fund && npm run build

# copy everything into nginx container
# nginx's stable line, pinned so that a build repeats
FROM nginx:1.30.6

# copy hugo files
COPY --from=hugo-builder /docs/public/ /docs/public/

# copy frontend assets
COPY --from=frontend-builder /front_end/dist /front_end/dist

# copy configuration file
COPY ./nginx_server/nginx_server.conf.template /etc/nginx/templates/default.conf.template

