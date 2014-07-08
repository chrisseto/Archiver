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

    def get(self, key, default=None):
        return self.raw_json.get(key, default)

    def __getitem__(self, key):
        return self.raw_json[key]
