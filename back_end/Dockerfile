FROM docker.io/gerlichlab/scshic_docker:release-1.3

WORKDIR /temp
COPY . /temp/install/

SHELL ["/bin/bash", "-c"]

# install python packages

RUN source activate flask &&\
    cd /temp/install &&\
    pip install -r requirements.txt

# install things from github

RUN source activate flask &&\
    pip install git+git://github.com/mirnylab/bioframe@40ca346f8726cf809a16fca4df21298f7c096dc3 &&\
    pip install git+git://github.com/mirnylab/cooltools@26b885356e5fd81dd6f34ef688edc45a020ca9d0 &&\
    pip install git+git://github.com/gerlichlab/ngs &&\
    pip install /temp/install/. 
    #Installs the repo itselve

CMD ["/bin/bash"]
