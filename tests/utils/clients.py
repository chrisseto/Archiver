import os
import copy
import mock
import random
import string


def rnd_str(length=10):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))


class MockDropBox(object):

    def __init__(self, token):
        self.listing = self.create_mock_dir()
        self.gets = []

    def get_file(self, path):
        assert path not in self.gets
        self.gets.append(path)

    def metadata(self, path, listing=None):
        if path == self.folder_name:
            return self.listing
        if not listing:
            listing = self.listing

        for item in listing['contents']:
            if item['is_dir']:
                try:
                    return self.metadata(path, item)
                except:
                    pass
            if path == item['path']:
                return item
        raise Exception('Path not found')

    def collect_calls(self, path=None):
        calls = []
        if path:
            listing = self.metadata(path)
        else:
            listing = self.listing
        for item in listing['contents']:
            if not item['is_dir']:
                calls.append((self, item['path']))
            else:
                calls.extend(self.collect_calls(item['path']))
        return calls

    def create_mock_item(self, parent=''):
        mock_item = {
            'is_dir': False,
            'bytes': random.randint(0, 5000000),
            'path': rnd_str()
        }
        mock_item['path'] = os.path.join(parent, mock_item['path'])
        return mock_item

    def create_mock_dir(self, parent=''):
        mock_dir = mock.MagicMock()
        mock_dir = {
            'is_dir': True,
            'bytes': 0,
            'path': rnd_str(),
            'contents': []
        }
        mock_dir['path'] = os.path.join(parent, mock_dir['path'])
        for _ in xrange(random.randint(3, 6)):
            if random.randint(0, 10) > 8:
                mock_dir['contents'].append(self.create_mock_dir(mock_dir['path']))
            else:
                mock_dir['contents'].append(self.create_mock_item(mock_dir['path']))
        return mock_dir


class MockKey(object):
    def __init__(self):
        self.key = rnd_str()
        self.name = self.key
        self.version_id = 'null'
        self.versions = self.get_versions()

    def get_contents_to_filename(self, name):
        pass

    def last_modified(self):
        return 7

    def get_version(self):
        clone = copy.deepcopy(self)
        clone.version_id = rnd_str()
        return clone

    def get_versions(self):
        return [
            self.get_version()
            for _ in
            xrange(random.randint(2, 5))
        ]


class MockBucket(object):
    def __init__(self):
        self.name = rnd_str()
        self.keys = [
            MockKey()
            for _ in
            xrange(random.randint(2, 5))
        ]

    def list(self):
        for key in self.keys:
            yield key

    def get_all_versions(self, prefix=None):
        if not prefix:
            versions = self.keys
            versions.extend(
                [
                    version
                    for key in self.keys
                    for version in key.versions
                ]
            )
            return versions
        for key in self.keys:
            if prefix == key.key:
                return [key] + key.versions

class MockClient(object):

    def __init__(self):
        self.id = rnd_str()
        self.key= {'token_key': "hello", 'token_secret':"world"}
        self.version_id = 'null'
        self.versions = self.get_versions()

    def get_contents_to_filename(self, name):
        pass

    def last_modified(self):
        return 7

    def get_version(self):
        clone = copy.deepcopy(self)
        clone.version_id = rnd_str()
        return clone

    def is_project(self):
        return True

    def get_versions(self):
        return [
            self.get_version()
            for _ in
            xrange(random.randint(2, 5))
        ]