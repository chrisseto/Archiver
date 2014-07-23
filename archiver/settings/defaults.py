### GENERAL SETTINGS ###
PORT = 7000
SENTRY_DSN = None
MAX_FILE_SIZE = None
HMAC_KEY = 'CHANGEME'
IGNORE_CALLBACK_SSL = False
REQUIRE_SIGNED_SUBMITIONS = False
BROKER_URL = 'amqp://archiver:archiver@192.168.111.112//'
CALLBACK_ADDRESS = [
    'http://192.168.111.111:7000/callback',
    'http://192.168.111.1:5000/api/v1/registration/finished/'
]


### Credentials Options ###
USERNAME = 'CHANGEME'  # Access key
PASSWORD = 'CHANGEME'  # Secret key
CONTAINER_NAME = 'CHANGEME'  # Bucket name


### LibCloud Options ###
LIBCLOUD_DRIVER = 's3_us_west_oregon'


#### FILE STORAGE OPTIONS ####
BACKEND = 's3'  # Options: S3,
CREATE_PARITIES = True
IGNORE_PARITIY_SIZE_LIMIT = False


#### FILE STORAGE LOCATIONS ####
FILES_DIR = 'Files/'
MANIFEST_DIR = 'Manifests/'
METADATA_DIR = 'File Metadata/'
DIRSTRUCT_DIR = 'Directory Structures/'
PARITY_DIR = 'Parities/'


### DEBUGGING OPTIONS ###
DEBUG = True
CELERY_SYNC = False  # Dont use celery just run everything synchronously
DUMP_INCOMING_JSON = False


#### CELERY OPTIONS ####
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
CELERY_ACKS_LATE = True
# Only process 5k jobs per hour
# This is to deal with API rate limiting
CELERY_DEFAULT_RATE_LIMIT = '5000/h'

#### CLONER OPTIONS ####
# Figshare
FIGSHARE_OAUTH_TOKENS = [
    'CLIENT ID',
    'CLIENT SECRET'
]
