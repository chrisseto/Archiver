import os
import json
import hashlib
import tempfile


class ServiceArchiver(object):

    ARCHIVES = None
    RESOURCE = None
    CHUNK_SIZE = 1024  # 1KB
    CUTOFF_SIZE = 1024 ** 2 * 500  # 500 MB

    def __init__(self, service):
        self.dirinfo = {
            'tempdir': service.parent.TEMP_DIR,
            'prefix': service.path(service.get(self.RESOURCE, ''))
        }
        self.cid = service.parent.cid

    def clone(self):
        raise NotImplementedError()

    @classmethod
    def chunked_file(cls, fobj, chunk_size=CHUNK_SIZE):
        while True:
            chunk = fobj.read(chunk_size)
            if not chunk:
                break
            yield chunk

    @classmethod
    def chunked_save(cls, fobj, to_loc):
        with open(to_loc, 'w+') as to_file:
            for chunk in cls.chunked_file(fobj):
                to_file.write(chunk)
        return to_loc

    @classmethod
    def sha256(cls, path):
        sha = hashlib.sha256()
        with open(path) as to_hash:
            for chunk in cls.chunked_file(to_hash):
                sha.update(chunk)
        return sha.hexdigest()

    @classmethod
    def md5(cls, path):
        md5 = hashlib.md5()
        with open(path) as to_hash:
            for chunk in cls.chunked_file(to_hash):
                md5.update(chunk)
        return md5.hexdigest()

    @classmethod
    def get_temp_file(cls):
        return tempfile.mkstemp()

    @classmethod
    def get_metadata(cls, path, name):
        return {
            "name": os.path.basename(name),
            "fullName": name,
            "md5": cls.md5(path),
            "sha256": cls.sha256(path),
            "size": os.path.getsize(path),
            "lastModified": os.path.getmtime(path)
        }

    @classmethod
    def write_json(cls, blob):
        fobj, path = cls.get_temp_file()
        fobj.write(json.dumps(blob))
        fobj.close()
        return path

    def build_directories(self, resource):
        full_path = os.path.join(self.dirinfo['tempdir'], self.dirinfo['prefix'], resource)
        full_dir = os.path.dirname(full_path)
        save_path = os.path.join(self.dirinfo['prefix'], resource)
        self.ensure_directory(full_dir)
        return full_path, save_path
