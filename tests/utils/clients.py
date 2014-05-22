import os
import mock
import random
import string


class MockDropBox(object):

    def __init__(self, token):
        self.listing = self.create_mock_dir()

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
                calls.append(item['path'])
            else:
                calls.extend(self.collect_calls(item['path']))
        return calls

    def create_mock_item(self, parent=''):
        mock_item = {
            'is_dir': False,
            'bytes': random.randint(0, 5000000),
            'path': ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        }
        mock_item['path'] = os.path.join(parent, mock_item['path'])
        return mock_item

    def create_mock_dir(self, parent=''):
        mock_dir = mock.MagicMock()
        mock_dir = {
            'is_dir': True,
            'bytes': 0,
            'path': ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)),
            'contents': []
        }
        mock_dir['path'] = os.path.join(parent, mock_dir['path'])
        for _ in xrange(random.randint(3, 6)):
            if random.randint(0, 10) > 9:
                mock_dir['contents'].append(self.create_mock_dir(mock_dir['path']))
            else:
                mock_dir['contents'].append(self.create_mock_item(mock_dir['path']))
        return mock_dir
