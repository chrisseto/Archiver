FROM ubuntu

RUN apt-get install -y python python-dev python-distribute python-pip
RUN pip install celery
RUN export C_FORCE_ROOT=1
WORKDIR /
ADD ./celeryq.py /celeryq.py
ENTRYPOINT celery -A celeryq worker -b $SERVICE_PORT_5672_TCP_ADDR
USER daemon
