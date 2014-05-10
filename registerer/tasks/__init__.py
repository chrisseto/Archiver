from celery import chord, group

from registerer import celery
from registerer.tasks import registration, callbacks


@celery.task
def register(node):
    header = [registration.create_registration.si(node)]

    for addon in node.addons:
        header.append(registration.register_addon.si(addon))

    for child in node.children:
        header.append(register.si(child))

    if node.is_child:
        c = group(header)
    else:
        c = chord(header, callbacks.registration_finish.si(node))

    c.link_error(callbacks.registration_failed.si(node))
    c.delay()
