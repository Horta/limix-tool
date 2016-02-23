FROM ubuntu:latest
RUN apt-get update
RUN apt-get install --yes wget build-essential
RUN wget http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh -O miniconda.sh
RUN chmod +x miniconda.sh
RUN ./miniconda.sh -b
ENV PATH /root/miniconda2/bin:$PATH
RUN conda update --yes conda
RUN conda install --yes python=2.7 numpy
RUN mkdir /limix-util
WORKDIR /limix-util
ADD . /limix-util
