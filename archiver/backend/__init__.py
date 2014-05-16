from archiver.settings import BACKEND

from . import storage

store = getattr(storage, BACKEND.capitalize())()
