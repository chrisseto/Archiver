FROM ubuntu:12.04

ADD local.py /local.py
RUN apt-get update && apt-get install -y python python-dev python-distribute python-pip git par2
RUN git clone https://github.com/chrisseto/archiver
WORKDIR /archiver
RUN cp /local.py archiver/settings/local.py
RUN pip install -r requirements.txt
RUN invoke setup
ENTRYPOINT ./Worker
USER daemon
