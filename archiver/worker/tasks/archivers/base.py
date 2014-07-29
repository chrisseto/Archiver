import os
import pytz
import logging
import hashlib
import tempfile
import datetime

from dateutil import parser


logger = logging.getLogger(__name__)


class ServiceArchiver(object):
    """Base class for archiving 3rd party services.
    Contains mostly helper functions.
    """
    ARCHIVES = None
    REQUIRED_KEYS = []
    CHUNK_SIZE = 1024  # 1KB
    CUTOFF_SIZE = 1024 ** 2 * 500  # 500 MB

    def __init__(self, service):
        self.cid = service.parent.id
        self.versions = service.versions
        self.force_parity = service.force_parity

        logger.info('Archiving {} for project {}'.format(self.ARCHIVES, self.cid))

        if self.versions:
            logger.info('Archiving {} versions'.format('all' if self.versions is True else self.versions))

        if self.force_parity:
            logger.info('Forcing parities for service {} of {}'.format(self.ARCHIVES, self.cid))

    def clone(self):
        """To be overridden by subclasses
        """
        raise NotImplementedError()

    @classmethod
    def chunked_file(cls, fobj, chunk_size=CHUNK_SIZE):
        """Read though files at iterators to save memory
        :param File fobj a file like object
        :param int chunk_size The amount of the file to load into memory
        """
        while True:
            chunk = fobj.read(chunk_size)
            if not chunk:
                break
            yield chunk

    @classmethod
    def chunked_save(cls, fobj):
        to_file, path = cls.get_temp_file()

        for chunk in cls.chunked_file(fobj):
            to_file.write(chunk)

        to_file.close()
        return path

    @classmethod
    def sha256(cls, path):
        """Computes the sha256 of a file in a memory efficient way
        :param str path The path to the file to hash
        """
        sha = hashlib.sha256()

        with open(path) as to_hash:
            for chunk in cls.chunked_file(to_hash):
                sha.update(chunk)

        return sha.hexdigest()

    @classmethod
    def md5(cls, path):
        """Computes the md5 of a file in a memory efficient way
        :param str path The path to the file to hash
        """
        md5 = hashlib.md5()

        with open(path) as to_hash:
            for chunk in cls.chunked_file(to_hash):
                md5.update(chunk)

        return md5.hexdigest()

    @classmethod
    def get_temp_file(cls):
        """Get a temporary file!
        :return: File Object and the path to it
        """
        fd, path = tempfile.mkstemp()
        return os.fdopen(fd, 'w'), path

    @classmethod
    def to_epoch(cls, dt):
        if not isinstance(dt, datetime.datetime):
            dt = parser.parse(dt)

        return (dt.replace(tzinfo=pytz.UTC) - datetime.datetime(1970, 1, 1).replace(tzinfo=pytz.UTC)).total_seconds()

    @classmethod
    def get_metadata(cls, path, name):
        return {
            "name": os.path.basename(name),
            "path": name,
            "md5": cls.md5(path),
            "sha256": cls.sha256(path),
            "size": os.path.getsize(path),
            "lastModified": os.path.getmtime(path)
        }
