from datetime import datetime
from celery import Celery


celery = Celery('celeryq', ampq='amqp://guest:guest@192.168.33.10///', backend='amqp')


@celery.task
def add(x, y):
    return x + y + 4


@celery.task
def fib(n):
    if n <= 1:
        return 1
    else:
        return fib(n-1) + fib(n-2)


@celery.task
def timed_fib(i):
    now = datetime.now()
    return fib(i), (datetime.now() - now).total_seconds()
