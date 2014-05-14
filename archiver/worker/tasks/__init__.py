from celery import chord, group

from archiver import celery
from archiver.worker.tasks import archival, callbacks


@celery.task
def archive(node):
    header = [archival.create_archive.si(node)]

    for addon in node.addons:
        header.append(archival.archive_addon.si(addon))

    for child in node.children:
        header.append(archive.si(child))

    if node.is_child:
        c = group(header)
    else:
        c = chord(header, callbacks.archival_finish.s(node))

    # c.link_error(callbacks.registration_failed.s(node))
    c.delay()
