FROM docker.io/ubuntu:bionic

WORKDIR /temp
COPY . /temp/install/

# Update and create base image (libz-dev is needed by pypairix)
RUN apt-get update -y &&\
    apt-get install apt-utils -y &&\
    apt-get install -y file bzip2 default-jre gcc g++ git make ssh unzip wget libz-dev &&\
    apt-get clean

# Install Anaconda
SHELL ["/bin/bash", "-c"]
RUN wget -q https://repo.anaconda.com/archive/Anaconda3-2019.10-Linux-x86_64.sh &&\
    bash Anaconda3-2019.10-Linux-x86_64.sh -b -p /home/anaconda3
ENV PATH="/home/anaconda3/bin:${PATH}"
RUN conda update -y conda &&\
    conda update -y conda-build

# Install flask environment
RUN conda env create -f /temp/install/flask.yml

# install python packages

RUN cd /temp/install &&\
    pip install -r requirements.txt

# install things from github

RUN pip install git+git://github.com/mirnylab/bioframe &&\
    pip install git+git://github.com/mirnylab/cooltools@26b885356e5fd81dd6f34ef688edc45a020ca9d0 &&\
    pip install git+git://github.com/gerlichlab/ngs

CMD ["/bin/bash"]
