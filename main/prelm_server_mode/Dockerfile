FROM ubuntu:14.04
MAINTAINER Shiran Dudy <dudy@ohsu.edu>
RUN apt-get update
RUN apt-get install -y wget
RUN apt-get install -y build-essential
RUN DEBIAN_FRONTEND=noniteractive apt-get install -y -q python-dev python-pip
RUN apt-get install -y zlib1g-dev
ENV Version openfst-1.6.9
ENV LD_LIBRARY_PATH /usr/local/lib
RUN wget http://openfst.org/twiki/pub/FST/FstDownload/${Version}.tar.gz
RUN tar -xzvf ${Version}.tar.gz
WORKDIR /${Version}
RUN ./configure --enable-far --enable-python --enable-lookahead-fsts --enable-special
RUN make
RUN make install
WORKDIR ../
ADD ./lm/requirements.txt /tmp/requirements.txt
RUN pip install -qr /tmp/requirements.txt
ADD ./lm /opt/lm/
ENV LD_LIBRARY_PATH "$LD_LIBRARY_PATH:/usr/local/lib/fst"
RUN rm /${Version}.tar.gz
RUN rm -rf /${Version}
RUN pip install openfst
WORKDIR /opt/lm
EXPOSE 5000
