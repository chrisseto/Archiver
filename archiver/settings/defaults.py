# QUEUE_NAME = 'celeryq'
FOREMAN_ADDRESS = 'http://10.0.2.2:7000'

DEBUG = True
CELERY_SYNC = False

#### FILE STORAGE OPTIONS ####
USE_S3 = True
ACCESS_KEY = 'CHANGEME'
SECRET_KEY = 'CHANGEME'
BUCKET_NAME = 'CHANGEME'

#### CELERY OPTIONS ####
BROKER_URL = 'amqp://guest:guest@192.168.33.10//'
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_RESULT_SERIALIZER = 'pickle'
CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']
CELERY_CHORD_PROPAGATES = False
CELERY_EAGER_PROPAGATES_EXCEPTIONS = CELERY_SYNC
CELERY_ALWAYS_EAGER = CELERY_SYNC
CELERY_RESULT_BACKEND = 'amqp'
CELERY_TASK_RESULT_EXPIRES = 18000  # 5 hours.
CELERY_TRACK_STARTED = True
CELERY_IMPORTS = 'archiver.worker.tasks'
CELERY_REDIRECT_STDOUTS_LEVEL = 'INFO'
