"""
Content transcoding classes & functions.

- :class:`BinaryContentHandler` basic transcoder for binary types that
  simply calls functions for encoding and decoding
- :class:`TextContentHandler` transcoder that translates binary bodies
  to text before calling functions that encode & decode text
- :class:`JSONTranscoder` intelligent transcoding for JSON bodies
- :class:`MsgPackTranscoder` intelligent transcoding for MsgPack bodies

The :class:`sprockets.mixins.mediatype.ContentMixin` uses transcoder
instances *under the hood*.  A transcoder is responsible for transforming
objects to and from the :class:`bytes` instances held in a request body.
This module implements the transcoders.

"""
import base64
import collections
import json
import uuid

from tornado import escape
try:
    import umsgpack
except ImportError as exc:  # pragma no cover
    umsgpack = None

    def MsgPackTranscoder(*args, **kwargs):
        raise exc


class BinaryContentHandler(object):
    """
    Pack and unpack binary types.

    :param str content_type: registered content type
    :param pack: function that transforms an object instance
        into :class:`bytes`
    :param unpack: function that transforms :class:`bytes`
        into an object instance

    This transcoder is a thin veneer around a pair of packing
    and unpacking functions.

    """

    def __init__(self, content_type, pack, unpack):
        super(BinaryContentHandler, self).__init__()
        self._pack = pack
        self._unpack = unpack
        self.content_type = content_type

    def to_bytes(self, inst_data, encoding=None):
        """
        Transform an object into :class:`bytes`.

        :param object inst_data: object to encode
        :param str encoding: ignored
        :returns: :class:`tuple` of the selected content
            type and the :class:`bytes` representation of
            `inst_data`

        """
        return self.content_type, self._pack(inst_data)

    def from_bytes(self, data_bytes, encoding=None, content_parameters=None):
        """
        Get an object from :class:`bytes`

        :param bytes data_bytes: stream of bytes to decode
        :param str encoding: ignored
        :param dict content_parameters: optional :class:`dict` of
            content type parameters from the :mailheader:`Content-Type`
            header
        :returns: decoded :class:`object` instance

        """
        return self._unpack(data_bytes)


class TextContentHandler(object):
    """
    Transcodes between textual and object representations.

    :param str content_type: registered content type
    :param dumps: function that transforms an object instance
        into a :class:`str`
    :param loads: function that transforms a :class:`str`
        into an object instance
    :param str default_encoding: encoding to apply when
        transcoding from the underlying body :class:`byte`
        instance

    This transcoder wraps functions that transcode between :class:`str`
    and :class:`object` instances.  In particular, it handles the
    additional step of transcoding into the :class:`byte` instances
    that tornado expects.

    """

    def __init__(self, content_type, dumps, loads, default_encoding):
        super(TextContentHandler, self).__init__()
        self._dumps = dumps
        self._loads = loads
        self.content_type = content_type
        self.default_encoding = default_encoding

    def to_bytes(self, data_dict, encoding=None):
        """
        Transform an object into :class:`bytes`.

        :param object inst_data: object to encode
        :param str encoding: character set used to encode the bytes
            returned from the ``dumps`` function.  This defaults to
            :attr:`default_encoding`
        :returns: :class:`tuple` of the selected content
            type and the :class:`bytes` representation of
            `inst_data`

        """
        selected = encoding or self.default_encoding
        content_type = '{}; charset="{}"'.format(self.content_type, selected)
        dumped = self._dumps(escape.recursive_unicode(data_dict))
        return content_type, dumped.encode(selected)

    def from_bytes(self, data, encoding=None, content_parameters=None):
        """
        Get an object from :class:`bytes`

        :param bytes data_bytes: stream of bytes to decode
        :param str encoding: character set used to decode the incoming
            bytes before calling the ``loads`` function.  This defaults
            to :attr:`default_encoding`
        :param dict content_parameters: optional :class:`dict` of
            content type parameters from the :mailheader:`Content-Type`
            header
        :returns: decoded :class:`object` instance

        """
        return self._loads(data.decode(encoding or self.default_encoding))


class JSONTranscoder(TextContentHandler):
    """
    JSON transcoder that understands common types.

    :param str content_type: the MIME content type that describes
        textual representations.  The default is ``application/json``
    :param str default_encoding: the default text character set.
        The sensible default here is ``utf-8`` but you can override
        it if necessary.
    :param dict loads_options: *kwargs* passed to :func:`json.loads`.
        This is useful if you want to pass in a custom load hook.

    This calls :func:`json.dumps` and :func:`json.loads` passing the
    :meth:`load_object_hook` and :meth:`dump_default` to implement
    encoding and decoding of common types.  You can sub-class and
    implement your own versions of these methods to add support for
    other types that you find yourself using a lot.

    The following types are supported:

    +-------------------------------+----------------------------------------+
    | Type                          | Format                                 |
    +===============================+========================================+
    | :class:`bytes`,               | Base64 encoded string.                 |
    | :class:`bytearray`,           |                                        |
    | :class:`memoryview`           |                                        |
    +-------------------------------+----------------------------------------+
    | :class:`datetime.datetime`    | ISO8601 date time in extended format.  |
    |                               | Includes separators, milliseconds, and |
    |                               | timezone designator.  Same as          |
    |                               | ``strftime('%Y-%m-%dT%H:%M:%S.%f%z')`` |
    +-------------------------------+----------------------------------------+
    | :class:`uuid.UUID`            | Same as ``str(value)``                 |
    +-------------------------------+----------------------------------------+

    """

    def __init__(self, content_type='application/json',
                 default_encoding='utf-8', loads_options=None):

        super(JSONTranscoder, self).__init__(content_type, self.dumps,
                                             self.loads, default_encoding)
        self.dump_options = {
            'default': self.dump_default,
            'separators': (',', ':'),
        }
        self.load_options = loads_options.copy() if loads_options else {}

    def dump_default(self, obj):
        """
        Called to encode unrecognized objects.

        :param object obj: object that is not of a recognized type
        :returns: the encoded object as a recognized type
        :raises TypeError: if the object cannot be encoded

        """
        if hasattr(obj, 'strftime'):
            return obj.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if isinstance(obj, (bytes, bytearray, memoryview)):
            return base64.b64encode(obj).decode('ASCII')

        raise TypeError(
            '{} is not JSON serializable'.format(obj.__class__.__name__))

    def dumps(self, data):
        """
        Transform an object into :class:`str`

        :param object data: object to encode
        :returns: :class:`str` representation of `data`

        """
        return json.dumps(data, **self.dump_options)

    def loads(self, data):
        """
        Transform a :class:`str` into an object.

        :param str data: representation to decode
        :returns: :class:`object` representation from `data`

        """
        return json.loads(data, **self.load_options)


if umsgpack is not None:

    class MsgPackTranscoder(BinaryContentHandler):
        """
        MsgPack transcoder that understands basic types.

        The :meth:`.normalize_datum` method is called to normalize
        each packed datum into something that ``umsgpack`` understands.

        - sequences & sets are converted to :class:`list` instances
        - :class:`datetime.datetime` instances are converted to
          :class:`str` instances containing the ISO8601 representation
        - :class:`uuid.UUID` instances are converted to :class:`str`
          instances via ``str(value)``
        - types mentioned in :data:`PACKABLE_TYPES` are left alone

        .. note::

           This transcoder is only available if you have the `umsgpack`_
           library installed.  You can install the library yourself or
           use ``sprockets.mixins.mediatype['msgpack']`` as a dependency

        .. _umsgpack: https://pypi.python.org/pypi/u-msgpack-python

        """

        PACKABLE_TYPES = (bool, int, float, str, bytes)
        """Types that umsgpack understands."""

        def __init__(self, content_type='application/msgpack'):
            super(MsgPackTranscoder, self).__init__(content_type, self.packb,
                                                    self.unpackb)

        def packb(self, data):
            """Pack `data` into a :class:`bytes` instance."""
            return umsgpack.packb(self.normalize_datum(data))

        def unpackb(self, data):
            """Unpack :class:`object` from a :class:`bytes` instance."""
            return umsgpack.unpackb(data)

        def normalize_datum(self, datum):
            """
            Convert `datum` into something packable.

            :param object datum: value to prepare for msgpack'ing
            :return: a packable version of `datum`
            :raise TypeError: if `datum` cannot be packed

            """

            if datum is None or isinstance(datum, self.PACKABLE_TYPES):
                return datum

            if hasattr(datum, 'strftime'):
                return datum.strftime('%Y-%m-%dT%H:%M:%S.%f%z')

            if isinstance(datum, uuid.UUID):
                return str(datum)

            if isinstance(datum, (bytearray, memoryview)):
                return bytes(datum)

            if isinstance(datum, (collections.Sequence, collections.Set)):
                return [self.normalize_datum(item) for item in datum]

            if isinstance(datum, collections.Mapping):
                out = {}
                for k, v in datum.items():
                    out[k] = self.normalize_datum(v)
                return out

            raise TypeError(
                '{} is not msgpackable'.format(datum.__class__.__name__))
