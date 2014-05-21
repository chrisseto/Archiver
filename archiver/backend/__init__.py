from archiver.settings import BACKEND

from storage import get_storagebackend, get_storagebackends


if isinstance(BACKEND, list):
    store = get_storagebackends(BACKEND)
else:
    store = get_storagebackend(BACKEND)

# print([cls for cls in vars()['BackEnd'].__subclasses__()])
