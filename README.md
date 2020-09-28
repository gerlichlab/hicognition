# HiCognition_flask
Flask server for HiCognition with Vue.js frontend.

## Project architecture

This is a single-page application (SPA) that uses nginx to serve the front-end to redirect api-calls from the front-end to a back-end flask-server.
Front-end files are located in [front_end](./front_end) and back-end files are located in [back_end](./back_end). 


## Branches
`stable` locked version, will be updated only once at the end of a sprint.

## Containers

`hicognition_flask` *private* container can be found on [dockerhub](https://hub.docker.com/repository/docker/gerlichlab/hicognition_flask). It is based on the `scshic_docker:release-1.3`.
- ubuntu installations are performed in scshic_docker
- `flask` minimal conda environment is set up in scshic_docker
- all pip installations (including flask) are performed here 
- ngs_base and all its tools are already added to PATH.

`higlass`: This container is the container tagged "latest" in `higlass/higlass-docker` and used purely as a viewer for data.

`nginx`: This container is used to serve the front-end as a static index.html file that includes all js-files during the node-based build process. It also redirects requests to /api/* to the hicognition_flask server.

`node`: Container that is temporarily used to build the front-end.
