FROM ubuntu

ADD local.py /local.py
RUN apt-get install -y python python-dev python-distribute python-pip git
RUN git clone https://github.com/chrisseto/archiver
WORKDIR /archiver
RUN cp /local.py archiver/settings/local.py
RUN pip install -r requirements.txt
RUN invoke setup
ENTRYPOINT invoke docker_worker
USER daemon
