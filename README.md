# HiCognition_flask
Flask server for HiCognition

## Branches
`stable` locked version, will be updated only once at the end of a sprint.

## Container
`hicognition_flask` *private* container can be found on [dockerhub](https://hub.docker.com/repository/docker/gerlichlab/hicognition_flask). It is based on the `scshic_docker:release-1.3`.
- ubuntu installations are performed in scshic_docker
- `flask` minimal conda environment is set up in scshic_docker
- all pip installations (including flask) are performed here 
- ngs_base and all its tools are already added to PATH.
