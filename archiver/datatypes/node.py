import os
import errno
import tempfile
from datetime import datetime

from .addon import Addon
from .. import validation


class Node(object):

    TEMP_DIR = tempfile.mkdtemp()

    @classmethod
    def from_json(cls, json, parent=None):
        if validation.validate_project(json):
            data = json['node']
            return cls(data['metadata']['id'], data['metadata']['title'],
                data['metadata']['description'], data['metadata']['contributors'], data['children'], data['addons'], raw=data, parent=parent)

    def __init__(self, id, title, description, contributors, children, addons, raw=None, parent=None):
        self.raw_json = raw
        self.parent = parent
        self.id = id
        self.title = title
        self.description = description
        self.contributors = contributors

        self.children = []
        for child in children:
            self.children.append(Node.from_json(child, parent=self))

        self.addons = []
        for addon in addons:
            self.addons.append(Addon(addon, self))

        self.registered_on = datetime.now()

    @property
    def path(self):
        if self.parent:
            return os.path.join(self.parent.path, 'children', self.id) + os.sep
        return os.path.join(self.id) + os.sep

    @property
    def is_child(self):
        return self.parent is not None

    @property
    def full_path(self):
        return os.path.join(self.TEMP_DIR, self.path)

    def make_dir(self):
        try:
            os.makedirs(self.full_path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    def metadata(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'contributors': self.contributors,
            'registered_on': str(self.registered_on)
        }
