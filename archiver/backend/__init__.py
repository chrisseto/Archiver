from archiver.settings import BACKEND

from storage import get_storagebackend, get_storagebackends

# Allows the specified backend(s) to be used by:
# from archiver.storage import store
# store.upload_file(someFile)
if isinstance(BACKEND, list):
    store = get_storagebackends(BACKEND)
else:
    store = get_storagebackend(BACKEND)
