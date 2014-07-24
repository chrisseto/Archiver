from archiver.exceptions import ValidationError

required_keys = {
    'raw': 'container',
    'container': ['metadata', 'children', 'services'],
    'container_metadata': ['id', 'title', 'contributors'],
    'service': ['token', 'access_key', 'access_token', 'password',
    'passphrase', 'token_key', 'token_secret', 'secret_key']
}

service_keys = {
    'github': ['access_token', 'repo', 'user'],
    'dataverse': ['username', 'password', 'dataverse', 'studyDoi'],
    's3': ['access_key', 'secret_key', 'bucket'],
    'figshare': ['token_key', 'token_secret', 'id'],
    'dropbox': ['access_token', 'folder'],
    'gitlab': [],  # TODO
}


def validate_project(data):
    if not required_keys['raw'] in data.keys():
        raise ValidationError('No container field')

    return _validate_container(data['container'])


def _validate_container(container):
    try:
        for key in required_keys['container']:
            if key not in container.keys():
                raise ValidationError('Missing field %s from container section' % key)
    except TypeError:
        raise ValidationError('Container is not a dictionary')

    for child in container['children']:
        _validate_container(child['container'])

    for service in container['services']:
        validate_service(service)

    return True


def validate_metadata(data):
    try:
        for key in required_keys['metadata']:
            if key not in data.keys():
                raise ValidationError('Missing field %s from metadata section' % key)
    except TypeError:
        raise ValidationError('Metadata is not a dictionary')

    if len(data['id']) > 61:
        raise ValidationError('Id is longer than 61 characters')

    return True


def validate_service(data):
    if len(data.keys()) != 1:
        raise ValidationError('Invalid service')

    service_name = data.keys()[0]
    service = data.values()[0]

    try:
        for key in service_keys[service_name]:
            try:
                assert service[key]
            except KeyError:
                raise ValidationError('Service %s is missing field %s' % (service_name, key))
            except AssertionError:
                raise ValidationError('Service %s can not have empty field %s' % (service_name, key))
    except KeyError:
        raise ValidationError('Unsupported service %s' % service_name)
    return True
