import copy

from nodes import *
from services import *


good_multi_children = copy.deepcopy(good)
good_multi_children['node']['children'] = [copy.deepcopy(good), copy.deepcopy(good)]

good_nested_children = copy.deepcopy(good_multi_children)
good_nested_children['node']['children'][0]['node']['children'] = [copy.deepcopy(good)]

good_children_service = copy.deepcopy(good_multi_children)
good_children_service['node']['children'][0] = copy.deepcopy(good_multi_service)


node_with_dropbox = copy.deepcopy(good)
node_with_dropbox['node']['services'][0] = dropbox_good
