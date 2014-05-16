import os

from dropbox.client import DropboxClient

from archiver import celery
from archiver.backend import push_file

from .utils import CUTOFF_SIZE, chunked_save, build_directories


def clone(addon):
    dirinfo = {
        'tempdir': addon.parent.TEMP_DIR,
        'prefix': addon.path('')  # Folder name will be included in Json response
    }
    # Todo 2nd level folders will have the top level folder in their paths
    addon.make_dir(addon['folder'])
    return clone_dropbox(addon['access_token'], addon['folder'], dirinfo)


def clone_dropbox(access_token, folder, dirinfo):
    client = DropboxClient(access_token)
    folder = client.metadata(folder)
    recurse(folder['contents'], client, dirinfo)


def recurse(contents, client, dirinfo):
    for item in contents:
        if item['is_dir']:
            if item['bytes'] > CUTOFF_SIZE:
                recurse.delay(contents, client, dirinfo)
            else:
                recurse(contents, client, dirinfo)
        if item['bytes'] > CUTOFF_SIZE:
            fetch.delay(item['path'], client, dirinfo)
        else:
            fetch(item['path'], client, dirinfo)


@celery.task
def fetch(path, client, dirinfo):
    fobj = client.get_file(path)

    path, save_loc = build_directories(dirinfo, path[1:])  # Remove beginning /

    chunked_save(fobj, path)
    push_file(path, save_loc)
