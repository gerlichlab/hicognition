FROM docker.io/gerlichlab/scshic_docker:dev-1.0

WORKDIR /temp
COPY . /temp/install/

SHELL ["/bin/bash", "-c"]

# install python packages

RUN source activate flask &&\
    cd /temp/install &&\
    pip install -r requirements.txt

# install things from github

RUN source activate flask &&\
    pip install git+git://github.com/mirnylab/bioframe@9af1b45e5000e23cdcf7dd94094f963d0141ed44 &&\
    pip install git+git://github.com/mirnylab/cooltools@78c18f8c4c7e7c088c95ed1d9d2cc0c7e632ba5c &&\
    pip install git+git://github.com/gerlichlab/ngs.git@hicognition-dev &&\
    pip install /temp/install/. 
    #Installs the repo itselve

CMD ["/bin/bash"]
