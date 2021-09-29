FROM continuumio/miniconda3:4.9.2
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG C.UTF-8  
ENV LC_ALL C.UTF-8

# Update and create base image
RUN apt-get update -y &&\
    apt-get install -y gcc g++ make libz-dev &&\
    apt-get clean

# Add yml file for conda environment
ADD conda_env.yml /temp/install/

# Add hicognition package for installation

ADD setup.py /temp/install/
ADD VERSION /temp/install/
ADD hicognition /temp/install/hicognition/

# install packages
RUN conda install mamba -n base -c conda-forge &&\
    mamba env update -n base --f /temp/install/conda_env.yml &&\
    mamba list > software_versions_conda.txt &&\
    # install version 0.3 of ngs
    pip install git+git://github.com/gerlichlab/ngs@v0.3b &&\
    # install pylola
    pip install git+git://github.com/Mittmich/pylola &&\
    # install hicognition 
    pip install /temp/install

# clean up install

RUN rm -rf /temp/install

WORKDIR /home

CMD ["/bin/bash"]
