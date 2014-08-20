import services


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
    'services': [
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

bad_service = {
    'container':
    {
        'metadata': {
            'id': '12345',
            'title': 'example project',
            'description': '',
            'contributors': [
                'john smith'
            ]
        },
        'services': [
            {
                'github': {
                    'user': 'chrisseto'
                }
            }
        ],
        'children': []
    }
}

unimplemented_service = {

}

good = {
    'container': {
        'metadata': {
            'id': '12345',
            'title': 'example project',
            'description': '',
            'contributors': [
                'john smith'
            ]
        },
        'services': [
            {
                'github': {
                    'access_token': 'some secret key',
                    'repo': 'archiver',
                    'user': 'chrisseto'
                },
            }
        ],
        'children': []
    }
}

good_with_gitlab = {
    'container': {
        'metadata': {
            'id': '12345',
            'title': 'example project',
            'description': '',
            'contributors': [
                'john smith'
            ]
        },
        'services': [
            {
                'gitlab': {
                    'user': 'cos',
                    'pid': 'osf'
                }
            }
        ],
        'children': []
    }
}


good_with_children = {
    'container':
    {
        'metadata': {
            'id': '12345',
            'title': 'example project',
            'description': '',
            'contributors': [
                'john smith'
            ]
        },
        'services': [
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
                'container': {
                    'metadata': {
                        'id': '12345',
                        'title': 'example project',
                        'description': '',
                        'contributors': [
                            'john smith'
                        ]
                    },
                    'services': [
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


good_multi_service = {
    'container':
    {
        'metadata': {
            'id': '12345',
            'title': 'example project',
            'description': '',
            'contributors': [
                'john smith'
            ]
        },
        'services': [
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

good_with_dataverse = {
    'container': {
        'metadata': {
            'id': '12345',
            'title': 'example project',
            'description': '',
            'contributors': [
                'john smith'
            ]
        },
        'services': [
            services.dataverse_good
        ],
        'children': []
    }
}
