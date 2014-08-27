import time

from . import validation
from .service import Service


class Container(object):

    @classmethod
    def from_json(cls, json, parent=None):
        if validation.validate_project(json):
            data = json['container']
            return cls(data['metadata']['id'], data['metadata']['title'],
                       data['metadata']['description'], data['metadata']['contributors'],
                       data['children'], data['services'], raw=data, parent=parent)

    def __init__(self, id, title, description, contributors, children, services, raw=None, parent=None):
        self.raw_json = raw
        self.parent = parent
        self.id = id
        self.title = title
        self.description = description
        self.contributors = contributors

        self.children = []
        for child in children:
            self.children.append(Container.from_json(child, parent=self))

        self.services = []
        for service in services:
            self.services.append(Service(service, self))

        self.registered_on = int(time.time())

    @property
    def is_child(self):
        return self.parent is not None

    def metadata(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'contributors': self.contributors,
            'archivedOn': str(self.registered_on)
        }
