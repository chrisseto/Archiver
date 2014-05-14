FROM ubuntu

ADD local.py /local.py
RUN apt-get install -y python python-dev python-distribute python-pip git
RUN git clone https://github.com/chrisseto/registerer
WORKDIR /registerer
RUN cp /local.py registerer/settings/local.py
RUN pip install -r requirements.txt
ENTRYPOINT invoke docker_worker
USER daemon
