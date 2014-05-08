from registerer import celery
from registerer.tasks.callbacks import check_completion
from registerer.tasks.registration import create_registration, register_addon


@celery.task
def register(node):
    create_registration.apply_async([node], link=partition_task.s())


@celery.task
def partition_task(node):
    for addon in node.addons:
        register_addon.delay(addon)

    #Assuming the we're supposed to register children
    for child in node.children:
        register.delay(child)

    #Both children and addons may be empty
    check_completion(node.id)
