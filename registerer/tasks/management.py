from registerer import celery
from registerer.tasks.callbacks import check_completion
from registerer.tasks.registration import create_registration, register_addon


@celery.task
def register(node, is_child=False):
    create_registration.apply_async(node, link=partition_task.s())


@celery.task
def partition_task(node):
    for addon in node.addons:
        register_addon.delay(addon)

    for child in node.children:
        register.delay(child, is_child=True)

    check_completion(node.id)
