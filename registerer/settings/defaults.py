QUEUE_NAME = 'celeryq'
RABBITMQ_ADDRESS = 'amqp://guest:guest@192.168.33.10//'

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

#### mongodb OPTIONS ####
BROKER_BACKEND = 'mongodb'
BROKER_HOST = "localhost"
BROKER_PORT = 27017
BROKER_USER = ""
BROKER_PASSWORD = ""
BROKER_VHOST = ""