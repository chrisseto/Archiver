FROM ubuntu

RUN apt-get install -y python python-dev python-distribute python-pip git
RUN pip install celery invoke
#RUN export C_FORCE_ROOT=1
RUN git clone https://github.com/chrisseto/Registerer
WORKDIR /Registerer
ENTRYPOINT invoke docker_worker
USER daemon
