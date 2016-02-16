FROM continuumio/miniconda:latest
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

WORKDIR /srv
ADD ./environment.yml /srv/environment.yml
RUN conda config --add channels https://conda.anaconda.org/horta
RUN conda env create
ENV CONDA_ACTIVATE "source activate limix-util"

RUN mkdir /limix-util
WORKDIR /limix-util
ADD . /limix-util
RUN $CONDA_ACTIVATE && python setup.py test
