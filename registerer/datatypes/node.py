from datetime import datetime

from .. import validator


class Node(object):

    @classmethod
    def from_json(cls, json):
        if validator.validate_project(json):
            data = json['node']
            return cls(data['metadata']['title'], data['metadata']['title'],
                data['metadata']['description'], data['contributors'], data['addons'], raw=data)

    def __init__(self, id, title, description, contributors, children, addons, raw=None):
        self.raw_json = raw
        self.id = id
        self.title = title
        self.description = description
        self.contributors = contributors
        self.children = []
        for child in children:
            self.children.append(Node.from_json(child))
        self.addons = addons
        self.registered_on = datetime.now()

    def metadata(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'contributors': self.contributors,
            'registered_on': self.registered_on
        }
