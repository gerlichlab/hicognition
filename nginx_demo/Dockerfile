# fetch the docs theme, a submodule
FROM ubuntu:24.04 AS theme-resolver

# Install git

RUN apt-get update -y &&\
    apt-get install -y git

ADD . /code

# only the pinned commit: the theme's history is 1.5 GB

RUN cd /code && git submodule update --init --recursive --depth 1

# build documentation
FROM ghcr.io/gohugoio/hugo:v0.169.0 AS hugo-builder

# copy files into container, for the image's user, which writes public/

COPY --from=theme-resolver --chown=hugo:hugo /code/documentation/hugo-site/ /docs/


# build hugo

RUN cd /docs/ && hugo

# build frontend
FROM node:24.22.2-trixie-slim AS frontend-builder

ADD ./front_end /front_end

ENV showcase=true

RUN cd /front_end && npm ci --no-audit --no-fund && npm run build

# copy everything into nginx container
# nginx's stable line, pinned so that a build repeats
FROM nginx:1.30.6

# copy hugo files
COPY --from=hugo-builder /docs/public/ /docs/public/

# copy frontend assets
COPY --from=frontend-builder /front_end/dist /front_end/dist

# copy main apge
COPY ./homepage /homepage

# copy configuration file
COPY ./nginx_demo/nginx_demo.conf.template /etc/nginx/templates/default.conf.template

