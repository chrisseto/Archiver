"""
Module: Storage
A dynamic storage module
Will handle uploading a cloned project to our choice of storage service
"""
import os

from base import StorageBackEnd
from exceptions import RemoteStorageError

__all__ = []

for mod in os.listdir(os.path.dirname(__file__)):
    root, ext = os.path.splitext(mod)
    if ext == '.py' and root not in ['__init__', 'base']:
        __all__.append(root)


from . import *


def get_storagebackend(service):
    for backend in StorageBackEnd.__subclasses__():
        if backend.USES == service:
            return backend()
    raise NotImplementedError('No backend for {}'.format(service))


def get_storagebackends(services):
    if len(services) == 1:
        return get_storagebackend(services[0])
    return StorageBackEndCollective(services)


class StorageBackEndCollective(StorageBackEnd):

    def __init__(self, services):
        self.backends = [
            get_storagebackend(backend)
            for backend
            in services
        ]
        if len(self.backends) < 1:
            raise Exception('No backends specified.')

    def get_file(self, path, backend=None):
        if backend:
            self._use_one('get_file', [path], backend)
        else:
            self._try_all('get_file', [path])

    def upload_file(self, from_loc, to, backend=None):
        if backend:
            self._use_one('push_file', [from_loc, to], backend)
        else:
            self._use_all('push_file', [from_loc, to])

    def push_directory(self, from_loc, to, backend=None):
        if backend:
            self._use_one('push_directory', [from_loc, to], backend)
        else:
            super(self, StorageBackEndCollective).push_directory(from_loc, to)

    def list_directory(self, directory, backend=None):
        if backend:
            return self._use_one('list_directory', [directory], backend)
        else:
            return self._try_all('list_directory', [directory])

    def get_metadata(self, id, backend=None):
        if backend:
            return self._use_one('get_metadata', [id], backend)
        else:
            return self._try_all('get_metadata', [id])

    def _try_all(self, method, args, index=0):
        if index > len(self.backends):
            raise RemoteStorageError('All backends failed!')
        try:
            return getattr(self.backends[index], method)(*args)
        except (NotImplementedError, RemoteStorageError):
            return self._try_all(method, args, index=index+1)

    def _use_all(self, method, args):
        for backend in self.backends:
            getattr(backend, method)(*args)

    def _use_one(self, method, args, backend):
        try:
            to_use = self.backends[backend]
        except TypeError:
            for end in self.backends:
                if end.USES == backend:
                    to_use = end
                    break
        if not to_use:
            raise Exception('Requested backend is not available')
        return getattr(to_use, method)(args)
