"""
Sprockets.Mixins.Media_type
===========================

"""
import json
import logging

import msgpack
from tornado import escape

version_info = (0, 0, 0)
__version__ = '.'.join(str(v) for v in version_info)

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


MIME_JSON = 'application/json'
MIME_JSON_UTF8 = 'application/json; charset=utf-8'
MIME_MSGPACK = 'application/msgpack'
SUPPORTED_ACCEPTS = {MIME_JSON, MIME_MSGPACK}
SUPPORTED_CONTENT_TYPES = {MIME_JSON, MIME_JSON_UTF8, MIME_MSGPACK}


class MediaTypeMixin(object):
    """Handles Content-Type and Accept header negotiation for you."""

    def is_valid_content_type(self):
        """Ensures the requests Content-Type is acceptable."""
        content_type = self.request.headers.get('Content-Type', '')
        return content_type.lower() in SUPPORTED_CONTENT_TYPES

    def is_valid_accept_header(self):
        """Checks that Accept header contains acceptable value.

        Raises an HTTPError with status 406 on failure. Defaults to
        application/msgpack.

        :return str: Accept header value.

        """
        accept = self.request.headers.get('Accept', MIME_MSGPACK).lower()
        return accept.lower() in SUPPORTED_ACCEPTS

    def decode_request(self):
        """Decode the request body according to the content-type header.

        :return dict: Decoded message body as python dict.

        """
        LOGGER.debug('Decoding the request')
        body = self.request.body

        if not body:
            LOGGER.debug('The request body is empty')
            return

        content_type = self.request.headers['Content-Type']

        if content_type in (MIME_JSON, MIME_JSON_UTF8):
            LOGGER.debug('Decoding the payload as JSON')
            return json.loads(body.decode('utf-8'))
        else:
            LOGGER.debug('Decoding the payload as MSGPACK')
            return escape.recursive_unicode(msgpack.loads(body))

    def write(self, payload):
        """Extend the write method to handle serialization."""
        accept = self.request.headers.get('Accept', MIME_MSGPACK)

        if accept in (MIME_JSON, MIME_JSON_UTF8):
            payload = json.dumps(payload).encode('utf-8')
            LOGGER.debug('Encoding payload as JSON')
            self.set_header('Content-Type', MIME_JSON_UTF8)
        else:
            payload = msgpack.dumps(payload)
            LOGGER.debug('Encoding payload as MSGPACK')
            self.set_header('Content-Type', MIME_MSGPACK)

        LOGGER.debug('Writing serialized payload')
        super(MediaTypeMixin, self).write(payload)
