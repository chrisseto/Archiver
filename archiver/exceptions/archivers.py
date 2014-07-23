class ArchiverError(Exception):
    pass


class FigshareArchiverError(ArchiverError):
    pass


class FigshareKeyError(ArchiverError):
    pass


class DataverseArchiverError(ArchiverError):
    pass


class DropboxArchiverError(ArchiverError):
    pass


class S3ArchiverError(ArchiverError):
    pass


class UnfetchableFile(ArchiverError):

    def __init__(self, reason, file, service):
        self.reason = reason
        self.file = file
        self.service = service
        Exception.__init__(self, reason, file, service)

    def to_json(self):
        return {
            'file': self.file,
            'reason': self.reason,
            'service': self.service
        }


class FileTooLargeError(UnfetchableFile):

    def __init__(self, file, service):
        UnfetchableFile.__init__(self, 'File is too large.', file, service)
