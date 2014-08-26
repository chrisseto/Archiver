import logging
import httplib as http

from tornado.web import HTTPError

from .archivers import *  # WWSD

logger = logging.getLogger(__name__)


class ValidationError(HTTPError):
    def __init__(self, reason):
        logger.debug('ValidationError raised. %s' % reason)
        super(ValidationError, self).__init__(http.BAD_REQUEST, reason=reason)
