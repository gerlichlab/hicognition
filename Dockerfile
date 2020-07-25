FROM docker.io/gerlichlab/scshic_docker:release-1.2

WORKDIR /temp
COPY . /temp/install/

# Update and create base image (libz-dev is needed by pypairix)
RUN apt-get update -y &&\
    apt-get install apt-utils -y &&\
    apt-get install -y libz-dev iproute2 curl iputils-ping &&\
    apt-get clean

SHELL ["/bin/bash", "-c"]

# Install flask environment
RUN conda env create -f /temp/install/flask.yml

# install python packages

RUN source activate flask &&\
    cd /temp/install &&\
    pip install -r requirements.txt

# install things from github

RUN source activate flask &&\
    pip install git+git://github.com/mirnylab/bioframe &&\
    pip install git+git://github.com/mirnylab/cooltools &&\
    pip install git+git://github.com/gerlichlab/ngs &&\
    pip install git+git://github.com/Mittmich/higlassupload

CMD ["/bin/bash"]
