# build documentation
FROM klakegg/hugo as hugo-builder

# copy files into container

ADD ./documentation/hugo-site/ /tmp/docs

RUN cd /tmp/docs && hugo

# build frontend
FROM node:14-buster as frontend-builder

ADD ./front_end /front_end

ENV showcase=true

RUN cd /front_end && npm install && npm run build

# copy everything into nginx container
FROM nginx

# copy hugo files

COPY --from=hugo-builder /tmp/docs/public/ /docs/public/

# copy frontend assets

COPY --from=frontend-builder /front_end/dist /front_end/dist

# copy configuration file
COPY ./nginx_demo/nginx_demo.conf /etc/nginx/conf.d/default.conf

# copy main apge

COPY ./homepage /homepage