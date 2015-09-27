"""
sprockets.mixins.media_type
===========================

"""
import logging

from ietfparse import algorithms, errors, headers
from tornado import escape, web


version_info = (1, 0, 4)
__version__ = '.'.join(str(v) for v in version_info)
logger = logging.getLogger(__name__)


class ContentSettings(object):
    """
    Content selection settings.

    An instance of this class is stashed as the ``_content_settings``
    attribute on the application object.  It contains the list of
    available content types and handlers associated with them.  Each
    handler implements a simple interface:

    - ``to_bytes(dict, encoding:str) -> bytes``
    - ``from_bytes(bytes, encoding:str) -> dict``

    Use the :func:`add_binary_content_type` and :func:`add_text_content_type`
    helper functions to modify the settings for the application.

    This class acts as a mapping from content-type string to the
    appropriate handler instance.  Add new content types and find
    handlers using the common ``dict`` syntax:

    .. code-block:: python

       class SomeHandler(web.RequestHandler):

          def get(self):
             settings = ContentSettings.from_application(self.application)
             response_body = settings['application/msgpack'].to_bytes(
                response_dict, encoding='utf-8')
             self.write(response_body)
             self.finish()

       def make_application():
          app = web.Application([web.url('/', SomeHandler)])
          add_binary_content_type(app, 'application/msgpack',
                                  msgpack.packb, msgpack.unpackb)
          add_text_content_type(app, 'application/json', 'utf-8',
                                json.dumps, json.loads)
          return app

    Of course, that is quite tedious, so use the :class:`.ContentMixin`
    instead.

    """

    def __init__(self):
        self._handlers = {}
        self._available_types = []
        self.default_content_type = None
        self.default_encoding = None

    def __getitem__(self, content_type):
        return self._handlers[content_type]

    def __setitem__(self, content_type, handler):
        if content_type in self._handlers:
            logger.warning('handler for %s already set to %r',
                           content_type, self._handers[content_type])
            return

        self._available_types.append(headers.parse_content_type(content_type))
        self._handlers[content_type] = handler

    def get(self, content_type, default=None):
        return self._handlers.get(content_type, default)

    @classmethod
    def from_application(cls, application):
        """Retrieve the content settings from an application."""
        if not hasattr(application, '_content_settings'):
            setattr(application, '_content_settings', cls())
        return application._content_settings

    @property
    def available_content_types(self):
        """
        List of the content types that are registered.

        This is a sequence of :class:`ietfparse.datastructures.ContentType`
        instances.

        """
        return self._available_types


def add_binary_content_type(application, content_type, pack, unpack):
    """
    Add handler for a binary content type.

    :param tornado.web.Application application: the application to modify
    :param str content_type: the content type to add
    :param pack: function that packs a dictionary to a byte string.
        ``pack(dict) -> bytes``
    :param unpack: function that takes a byte string and returns a
        dictionary.  ``unpack(bytes) -> dict``

    """
    settings = ContentSettings.from_application(application)
    settings[content_type] = _BinaryContentHandler(content_type, pack, unpack)


def add_text_content_type(application, content_type, default_encoding,
                          dumps, loads):
    """
    Add handler for a text content type.

    :param tornado.web.Application application: the application to modify
    :param str content_type: the content type to add
    :param str default_encoding: encoding to use when one is unspecified
    :param dumps: function that dumps a dictionary to a string.
        ``dumps(dict, encoding:str) -> str``
    :param loads: function that loads a dictionary from a string.
        ``loads(str, encoding:str) -> dict``

    """
    settings = ContentSettings.from_application(application)
    settings[content_type] = _TextContentHandler(content_type, dumps, loads,
                                                 default_encoding)


def set_default_content_type(application, content_type, encoding=None):
    """
    Store the default content type for an application.

    :param tornado.web.Application application: the application to modify
    :param str content_type: the content type to default to
    :param str|None encoding: encoding to use when one is unspecified

    """
    settings = ContentSettings.from_application(application)
    settings.default_content_type = content_type
    settings.default_encoding = encoding


class ContentMixin(object):
    """
    Mix this in to add some content handling methods.

    .. code-block:: python

       class MyHandler(ContentMixin, web.RequestHandler):
          def post(self):
             body = self.get_request_body()
             # do stuff --> response_dict
             self.send_response(response_dict)
             self.finish()

    :meth:`get_request_body` will deserialize the request data into
    a dictionary based on the :http:header:`Content-Type` request
    header.  Similarly, :meth:`send_response` takes a dictionary,
    serializes it based on the :http:header:`Accept` request header
    and the application :class:`ContentSettings`, and writes it out,
    using ``self.write()``.

    """

    def initialize(self):
        super(ContentMixin, self).initialize()
        self._request_body = None
        self._best_response_match = None

    def get_response_content_type(self):
        """Figure out what content type will be used in the response."""
        if self._best_response_match is None:
            settings = ContentSettings.from_application(self.application)
            acceptable = headers.parse_http_accept_header(
                self.request.headers.get(
                    'Accept',
                    settings.default_content_type
                    if settings.default_content_type else '*/*'))
            try:
                selected, _ = algorithms.select_content_type(
                    acceptable, settings.available_content_types)
                self._best_response_match = '/'.join(
                    [selected.content_type, selected.content_subtype])
            except errors.NoMatch:
                self._best_response_match = settings.default_content_type

        return self._best_response_match

    def get_request_body(self):
        """
        Fetch (and cache) the request body as a dictionary.

        :raise web.HTTPError: if the content type cannot be decoded.
            The status code is set to 415 Unsupported Media Type

        """
        if self._request_body is None:
            settings = ContentSettings.from_application(self.application)
            content_type_header = headers.parse_content_type(
                self.request.headers.get('Content-Type',
                                         settings.default_content_type))
            content_type = '/'.join([content_type_header.content_type,
                                     content_type_header.content_subtype])
            try:
                handler = settings[content_type]
                self._request_body = handler.from_bytes(self.request.body)

            except KeyError:
                raise web.HTTPError(415, 'cannot decode body of type %s',
                                    content_type)

        return self._request_body

    def send_response(self, body, set_content_type=True):
        """
        Serialize and send ``body`` in the response.

        :param dict body: the body to serialize
        :param bool set_content_type: should the :http:header:`Content-Type`
            header be set?  Defaults to :data:`True`

        """
        settings = ContentSettings.from_application(self.application)
        handler = settings[self.get_response_content_type()]
        content_type, data_bytes = handler.to_bytes(body)
        if set_content_type:
            self.set_header('Content-Type', content_type)
        self.write(data_bytes)


class _BinaryContentHandler(object):

    def __init__(self, content_type, pack, unpack):
        self._pack = pack
        self._unpack = unpack
        self.content_type = content_type

    def to_bytes(self, data_dict, encoding=None):
        return self.content_type, self._pack(data_dict)

    def from_bytes(self, data, encoding=None):
        return self._unpack(data)


class _TextContentHandler(object):

    def __init__(self, content_type, dumps, loads, default_encoding):
        self._dumps = dumps
        self._loads = loads
        self.content_type = content_type
        self.default_encoding = default_encoding

    def to_bytes(self, data_dict, encoding=None):
        selected = encoding or self.default_encoding
        content_type = '{0}; charset="{1}"'.format(self.content_type, selected)
        dumped = self._dumps(escape.recursive_unicode(data_dict))
        return content_type, dumped.encode(selected)

    def from_bytes(self, data, encoding=None):
        return self._loads(data.decode(encoding or self.default_encoding))
