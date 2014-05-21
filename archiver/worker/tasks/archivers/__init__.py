import os

from base import ServiceArchiver


__all__ = []

for mod in os.listdir(os.path.dirname(__file__)):
    root, ext = os.path.splitext(mod)
    if ext == '.py' and root not in ['__init__', 'base']:
        __all__.append(root)


from . import *


def get_archiver(service):
    for archiver in ServiceArchiver.__subclasses__():
        if archiver.ARCHIVES == service:
            return archiver
    raise NotImplementedError('No archiver for {}'.format(service))
