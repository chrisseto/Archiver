import os
import errno


class ServiceArchiver(object):

    ARCHIVES = None
    RESOURCE = None
    CHUNK_SIZE = 1024  # 1KB
    CUTOFF_SIZE = 1024 ** 2 * 500  # 500 MB

    def __init__(self, addon):
        self.dirinfo = {
            'tempdir': addon.parent.TEMP_DIR,
            'prefix': addon.path(addon.get(self.RESOURCE, ''))
        }

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
    def ensure_directory(cls, directory):
        try:
            os.makedirs(directory)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    def build_directories(self, resource):
        full_path = os.path.join(self.dirinfo['tempdir'], self.dirinfo['prefix'], resource)
        full_dir = os.path.dirname(full_path)
        save_path = os.path.join(self.dirinfo['prefix'], resource)
        self.ensure_directory(full_dir)
        return full_path, save_path
