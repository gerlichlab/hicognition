# Resolve learn submodule
FROM ubuntu:20.04 as theme-resolver

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
FROM node:14-buster as frontend-builder

ADD ./front_end /front_end

ENV showcase=true

RUN cd /front_end && npm install && npm run build

# copy everything into nginx container
FROM nginx

# copy hugo files
COPY --from=hugo-builder /docs/public/ /docs/public/

# copy frontend assets
COPY --from=frontend-builder /front_end/dist /front_end/dist

# copy configuration file
COPY ./nginx_server/nginx_server.conf.template /etc/nginx/templates/default.conf.template

