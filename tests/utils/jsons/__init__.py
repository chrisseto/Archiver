import copy

from nodes import *
from addons import *


good_multi_children = copy.deepcopy(good)
good_multi_children['node']['children'] = [copy.deepcopy(good), copy.deepcopy(good)]

good_nested_children = copy.deepcopy(good_multi_children)
good_nested_children['node']['children'][0]['node']['children'] = [copy.deepcopy(good)]

good_children_addon = copy.deepcopy(good_multi_children)
good_children_addon['node']['children'][0] = copy.deepcopy(good_multi_addon)


node_with_dropbox = copy.deepcopy(good)
node_with_dropbox['node']['addons'][0] = dropbox_good
