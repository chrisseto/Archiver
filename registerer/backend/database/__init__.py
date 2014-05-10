"""
Module: registerer.backend.database
This module with deal with the database backend.
This includes but is not limitted to:
    Keeping track of archives
    Tracking the status of current nodes being registered

"""
from pymongo import MongoClient
from bson import ObjectId

from ...settings import defaults

mongo_uri = 'mongodb://localhost:{port}'.format(port=defaults.DB_PORT)
client = MongoClient(mongo_uri)

db = client[defaults.DB_NAME]

if defaults.DB_USER and defaults.DB_PASSWORD:
    db.authenticate(defaults.DB_USER, defaults.DB_PASSWORD)


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