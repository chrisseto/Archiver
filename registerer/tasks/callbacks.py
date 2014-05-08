from registerer import celery


@celery.task
def registration_failed(id):
    pass


@celery.task
def registration_finish(id):
    pass


@celery.task
def check_completion(id):
    pass
