"""
Module: registerer.backend.database
This module with deal with the database backend.
This includes but is not limitted to:
    Keeping track of archives
    Tracking the status of current nodes being registered

"""
import logging
from bson import ObjectId
from pymongo import MongoClient

from registerer import settings

logger = logging.getLogger(__name__)

try:
    mongo_uri = 'mongodb://{host}:{port}'.format(port=settings.DB_PORT, host=settings.DB_HOST)
    client = MongoClient(mongo_uri)

    db = client[settings.DB_NAME]

    if settings.DB_USER and settings.DB_PASSWORD:
        db.authenticate(settings.DB_USER, settings.DB_PASSWORD)
except Exception as e:
    logger.error('Could not connect to database.')
    logger.warning('Proceeding without connection')


def set_up_storage(schemas, storage_class, prefix='', addons=None, *args, **kwargs):
    '''Setup the storage backend for each schema in ``schemas``.
    note::
        ``**kwargs`` are passed to the constructor of ``storage_class``

    Example usage with modular-odm and pymongo:
    ::

        >>> from pymongo import MongoClient
        >>> from modularodm.storage import MongoStorage
        >>> client = MongoClient(port=20771)
        >>> db = client['mydb']
        >>> models = [User, Node, addons]
        >>> set_up_storage(models, MongoStorage, db=db)
    '''
    # import pdb; pdb.set_trace()
    _schemas = []
    _schemas.extend(schemas)

    for addon in (addons or []):
        _schemas.extend(addon.models)

    for schema in _schemas:
        collection = "{0}{1}".format(prefix, schema._name)
        schema.set_storage(storage_class(collection=collection, **kwargs))
    return None
