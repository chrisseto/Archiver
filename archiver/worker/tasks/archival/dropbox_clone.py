import os

from dropbox.client import DropboxClient

from archiver import celery
from archiver.backend import push_file

from .utils import CUTOFF_SIZE, chunked_save, ensure_directory


def clone(addon):
    addon.make_dir(addon['folder'])
    return clone_dropbox(addon['access_token'], addon['folder'], addon.parent.TEMP_DIR)


def clone_dropbox(access_token, folder, savedir_prefix):
    client = DropboxClient(access_token)
    folder = client.metadata(folder)
    recurse(folder['contents'], client, savedir_prefix)


def recurse(contents, client, savedir_prefix):
    for item in contents:
        if item['is_dir']:
            if item['bytes'] > CUTOFF_SIZE:
                recurse.delay(contents, client, savedir_prefix)
            else:
                recurse(contents, client, savedir_prefix)
        if item['bytes'] > CUTOFF_SIZE:
            fetch.delay(item['path'], client, savedir_prefix)
        else:
            fetch(item['path'], client, savedir_prefix)


@celery.task
def fetch(path, client, savedir_prefix):
    fobj = client.get_file(path)

    path = path[1:]  # Remove begining /
    full_dir = os.path.join(savedir_prefix, os.path.dirname(path))
    full_path = os.path.join(savedir_prefix, path)

    ensure_directory(full_dir)
    chunked_save(fobj, full_path)

    push_file(full_path, path)
