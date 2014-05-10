QUEUE_NAME = 'celeryq'
RABBITMQ_ADDRESS = 'amqp://guest:guest@192.168.33.10//'

#### FILE STORAGE OPTIONS ####
USE_S3 = True
ACCESS_KEY = 'CHANGEME'
SECRET_KEY = 'CHANGEME'
BUCKET_NAME = 'CHANGEME'

#### CELERY OPTIONS ####
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_BACKEND = "mongodb"
CELERY_MONGODB_BACKEND_SETTINGS = {
    # Shouldn't need these - defaults are correct.
    "host": "localhost",
    "port": 27017,
    "database": "celery",
    "taskmeta_collection": "messages",
}
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']

#### mongodb OPTIONS ####
BROKER_BACKEND = 'mongodb'
BROKER_HOST = "localhost"
BROKER_PORT = 27017
BROKER_USER = ""
BROKER_PASSWORD = ""
BROKER_VHOST = ""

