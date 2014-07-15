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
        valid = valid and bool(data['id']) and len(data['id']) < 61
        valid = valid and bool(data['title'])
        valid = valid and bool(data['contributors'])
        return valid
    except KeyError:
        return False


def _validate_github(data):
    try:
        valid = data is not None
        valid = valid and bool(data['access_token'])
        valid = valid and bool(data['repo'])
        valid = valid and bool(data['user'])
        return valid
    except KeyError:
        return False


def _validate_dataverse(data):
    try:
        valid = data is not None
        valid = valid and bool(data['username'])
        valid = valid and bool(data['password'])
        valid = valid and bool(data['dataverse'])
        valid = valid and bool(data['studyDoi'])
        return valid
    except KeyError:
        return False


def _validate_dropbox(data):
    try:
        valid = data is not None
        valid = valid and bool(data['access_token'])
        valid = valid and bool(data['folder'])
        return valid
    except KeyError:
        return False


def _validate_figshare(data):
    try:
        valid = data is not None
        valid = valid and bool(data['token_key'])
        valid = valid and bool(data['token_secret'])
        valid = valid and bool(data['id'])
        return valid
    except KeyError:
        return False


def _validate_s3(data):
    try:
        valid = data is not None
        valid = valid and bool(data['access_key'])
        valid = valid and bool(data['secret_key'])
        valid = valid and bool(data['bucket'])
        return valid
    except KeyError:
        return False


def _validate_service(data):
    try:
        valid = data is not None
        if data['github']:
            valid = valid and _validate_github(data['github'])
        if data['dataverse']:
            valid = valid and _validate_dataverse(data['dataverse'])
        if data['dropbox']:
            valid = valid and _validate_dropbox(data['dropbox'])
        if data['figshare']:
            valid = valid and _validate_figshare(data['figshare'])
        if data['s3']:
            valid = valid and _validate_s3(data['s3'])
        return valid
    except KeyError:
        pass
    raise ValidationError('missing service segment')