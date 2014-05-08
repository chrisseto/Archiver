from app import celery


@celery.task
def registration_failed(id):
    pass


@celery.task
def registration_finish(id):
    pass
