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
    pip install git+git://github.com/mirnylab/bioframe &&\
    pip install git+git://github.com/mirnylab/cooltools &&\
    pip install git+git://github.com/gerlichlab/ngs &&\
    pip install git+git://github.com/Mittmich/higlassupload

CMD ["/bin/bash"]
