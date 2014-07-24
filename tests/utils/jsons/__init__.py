import copy

from containers import *
from services import *


good_multi_children = copy.deepcopy(good)
good_multi_children['container']['children'] = [copy.deepcopy(good), copy.deepcopy(good)]

good_nested_children = copy.deepcopy(good_multi_children)
good_nested_children['container']['children'][0]['container']['children'] = [copy.deepcopy(good)]

good_children_service = copy.deepcopy(good_multi_children)
good_children_service['container']['children'][0] = copy.deepcopy(good_multi_service)


container_with_dropbox = copy.deepcopy(good)
container_with_dropbox['container']['services'][0] = dropbox_good

container_with_figshare = copy.deepcopy(good)
container_with_figshare['container']['services'][0] = figshare_good
