"""
Content transcoding classes & functions.

The :class:`sprockets.mixins.mediatype.ContentMixin` uses transcoder
instances *under the hood*.  A transcoder is responsible for transforming
objects to and from the :class:`bytes` instances held in a request body.
This module implements the transcoders.

"""
import json

from tornado import escape


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

    def from_bytes(self, data_bytes, encoding=None):
        """
        Get an object from :class:`bytes`

        :param bytes data_bytes: stream of bytes to decode
        :param str encoding: ignored
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

    def from_bytes(self, data, encoding=None):
        """
        Get an object from :class:`bytes`

        :param bytes data_bytes: stream of bytes to decode
        :param str encoding: character set used to decode the incoming
            bytes before calling the ``loads`` function.  This defaults
            to :attr:`default_encoding`
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

    This calls :func:`json.dumps` and :func:`json.loads` passing the
    :meth:`load_object_hook` and :meth:`dump_default` to implement
    encoding and decoding of common types.  You can sub-class and
    implement your own versions of these methods to add support for
    other types that you find yourself using a lot.

    """

    def __init__(self, content_type='application/json',
                 default_encoding='utf-8'):

        super(JSONTranscoder, self).__init__(content_type, self.dumps,
                                             self.loads, default_encoding)
        self.dump_options = {
            'default': self.dump_default,
            'separators': (',', ':'),
        }
        self.load_options = {
            'object_hook': self.load_object_hook,
        }

    def load_object_hook(self, obj):
        """
        Called with objects as they are decoded.

        :param object obj: object that was decoded.  This is a
            :class:`list` or :class:`dict`.
        :returns: possibly modified version of `obj`

        """
        return obj

    def dump_default(self, obj):
        """
        Called to encode unrecognized objects.

        :param object obj: object that is not of a recognized type
        :returns: the encoded object as a recognized type
        :raises TypeError: if the object cannot be encoded

        """
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
