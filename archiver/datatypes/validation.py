from archiver.exceptions import ValidationError


def validate_project(data):
    try:
        if data['container']:
            return _validate_project(data['container'])
    except KeyError:
        pass
    raise ValidationError('missing container segment')


def _validate_project(container):
    try:
        if _validate_metadata(container['metadata']):
            for child in container['children']:
                if not _validate_project(child['container']):
                    raise ValidationError('bad child')
            for service in container['services']:
                if not _validate_service(service):
                    raise ValidationError('bad service')
            return True
    except (KeyError, TypeError):
        raise ValidationError('malformed data')
    raise ValidationError('improperly formatted data')


def _validate_metadata(data):
    try:
        valid = data is not None
        valid = valid and bool(data['id'])
        valid = valid and bool(data['title'])
        valid = valid and bool(data['contributors'])
        return valid
    except KeyError:
        return False


#TODO
def _validate_service(data):
    return True
