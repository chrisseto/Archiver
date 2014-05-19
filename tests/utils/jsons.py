import copy


empty = {}

bad_structure = {
    'metadata': {
        'id': '12345',
        'title': 'example project',
        'description': '',
        'contributors': [
            'john smith'
        ]
    },
    'addons': [
        {
            'github': {
                'access_token': 'some secret key',
                'repo': 'archiver',
                'user': 'chrisseto'
            }
        }
    ],
    'children': []
}

bad_children = {}

bad_addon = {
    'node':
    {
        'metadata': {
            'id': '12345',
            'title': 'example project',
            'description': '',
            'contributors': [
                'john smith'
            ]
        },
        'addons': [
            {
                'github': {
                    'user': 'chrisseto'
                }
            }
        ],
        'children': []
    }
}

unimplemented_addon = {

}

good = {
    'node':
    {
        'metadata': {
            'id': '12345',
            'title': 'example project',
            'description': '',
            'contributors': [
                'john smith'
            ]
        },
        'addons': [
            {
                'github': {
                    'access_token': 'some secret key',
                    'repo': 'archiver',
                    'user': 'chrisseto'
                }
            }
        ],
        'children': []
    }
}


good_with_children = {
    'node':
    {
        'metadata': {
            'id': '12345',
            'title': 'example project',
            'description': '',
            'contributors': [
                'john smith'
            ]
        },
        'addons': [
            {
                'github': {
                    'access_token': 'some secret key',
                    'repo': 'archiver',
                    'user': 'chrisseto'
                }
            }
        ],
        'children': [
            {
                'node': {
                    'metadata': {
                        'id': '12345',
                        'title': 'example project',
                        'description': '',
                        'contributors': [
                            'john smith'
                        ]
                    },
                    'addons': [
                        {
                            'github': {
                                'access_token': 'some secret key',
                                'repo': 'archiver',
                                'user': 'chrisseto'
                            }
                        }
                    ],
                    'children': []
                }
            }
        ]
    }
}

good_multi_children = copy.deepcopy(good)
good_multi_children['node']['children'] = [copy.deepcopy(good), copy.deepcopy(good)]

good_nested_children = copy.deepcopy(good_multi_children)
good_nested_children['node']['children'][0]['node']['children'] = [copy.deepcopy(good)]

good_multi_addon = {
    'node':
    {
        'metadata': {
            'id': '12345',
            'title': 'example project',
            'description': '',
            'contributors': [
                'john smith'
            ]
        },
        'addons': [
            {
                'github': {
                    'access_token': 'some secret key',
                    'repo': 'archiver',
                    'user': 'chrisseto'
                },
            },
            {
                's3': {
                    'access_key': 'Some key',
                    'secret_key': 'Another Key',
                    'bucket': 'a bucket name'
                }
            }
        ],
        'children': []
    }
}

good_children_addon = copy.deepcopy(good_multi_children)
good_children_addon['node']['children'][0] = copy.deepcopy(good_multi_addon)
