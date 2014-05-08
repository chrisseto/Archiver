FROM ubuntu

RUN apt-get install -y python python-dev python-distribute python-pip git
#RUN export C_FORCE_ROOT=1
RUN git clone https://github.com/chrisseto/Registerer
WORKDIR /Registerer
RUN pip install -r requirements.txt
ENTRYPOINT invoke docker_worker
#ENTRYPOINT celery -A registerer.celery worker -I registerer.tasks -b $SERVICE_PORT_5672_TCP_ADDR
USER daemon
