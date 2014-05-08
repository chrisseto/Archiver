from app import celery
from registerer.tasks.registration import create_registration, register_addons


@celery.task
def register(node):
    create_registration.apply_async(node, link=register_addons.s(node.addon))


def partition_task(node):
    pass
