from dropbox.client import DropboxClient

from archiver import celery
from archiver.backend import push_file

from .utils import CUTOFF_SIZE, chunked_save


def clone_dropbox(addon):
    client = DropboxClient(addon['access_token'])
    folder = client.metadata(addon['folder'])
    recurse(folder['contents'], client)


def recurse(contents, client, addon):
    for item in contents:
        if item['is_dir']:
            if item['bytes'] > CUTOFF_SIZE:
                recurse.delay(contents, client, addon)
            else:
                recurse(contents, client)
        if item['bytes'] > CUTOFF_SIZE:
            fetch.delay(item['path'], client, addon)
        else:
            fetch(item['path'], client, addon)


@celery.task
def fetch(path, client, addon):
    fobj = client.get_file(path)
    to_loc = addon.full_path(path)
    chunked_save(fobj, )
    push_file(to_loc, addon.path(path))


#export as clone
clone = clone_dropbox
