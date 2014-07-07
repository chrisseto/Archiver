import os
import errno


class Service(object):

    def __init__(self, json, parent):
        self.service, self.raw_json = json.items()[0]
        self.parent = parent

    @property
    def versions(self):
        return self.raw_json.get('versions')

    @property
    def force_parity(self):
        return self.raw_json.get('forceParity', False)

    def path(self, extra):
        return os.path.join(self.parent.path, 'services', self.service, extra) + os.sep

    def full_path(self, extra):
        return os.path.join(self.parent.TEMP_DIR, self.path(extra))

    def make_dir(self, extra):
        try:
            os.makedirs(self.full_path(extra))
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    def get(self, key, default=None):
        return self.raw_json.get(key, default)

    def __getitem__(self, key):
        return self.raw_json[key]
