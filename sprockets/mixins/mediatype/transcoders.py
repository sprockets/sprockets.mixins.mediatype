"""
Bundled media type transcoders.

- :class:`.JSONTranscoder` implements JSON encoding/decoding

"""
import base64
import json
import uuid

from sprockets.mixins.mediatype import handlers


class JSONTranscoder(handlers.TextContentHandler):
    """
    JSON transcoder instance.

    :param str content_type: the content type that this encoder instance
        implements. If omitted, ``application/json`` is used. This is
        passed directly to the ``TextContentHandler`` initializer.
    :param str default_encoding: the encoding to use if none is specified.
        If omitted, this defaults to ``utf-8``. This is passed directly to
        the ``TextContentHandler`` initializer.

    This JSON encoder uses :func:`json.loads` and :func:`json.dumps` to
    implement JSON encoding/decoding.  The :meth:`dump_object` method is
    configured to handle types that the standard JSON module does not
    support.

    .. attribute:: dump_options

       Keyword parameters that are passed to :func:`json.dumps` when
       :meth:`.dumps` is called.  By default, the :meth:`dump_object`
       method is enabled as the default object hook.

    .. attribute:: load_options

       Keyword parameters that are passed to :func:`json.loads` when
       :meth:`.loads` is called.

    """

    def __init__(self, content_type='application/json',
                 default_encoding='utf-8'):
        super(JSONTranscoder, self).__init__(content_type, self.dumps,
                                             self.loads, default_encoding)
        self.dump_options = {
            'default': self.dump_object,
            'separators': (',', ':'),
        }
        self.load_options = {}

    def dumps(self, obj):
        """
        Dump a :class:`object` instance into a JSON :class:`str`

        :param object obj: the object to dump
        :return: the JSON representation of :class:`object`

        """
        return json.dumps(obj, **self.dump_options)

    def loads(self, str_repr):
        """
        Transform :class:`str` into an :class:`object` instance.

        :param str str_repr: the UNICODE representation of an object
        :return: the decoded :class:`object` representation

        """
        return json.loads(str_repr, **self.load_options)

    def dump_object(self, obj):
        """
        Called to encode unrecognized object.

        :param object obj: the object to encode
        :return: the encoded object
        :raises TypeError: when `obj` cannot be encoded

        This method is passed as the ``default`` keyword parameter
        to :func:`json.dumps`.  It provides default representations for
        a number of Python language/standard library types.

        +----------------------------+---------------------------------------+
        | Python Type                | String Format                         |
        +----------------------------+---------------------------------------+
        | :class:`bytes`,            | Base64 encoded string.                |
        | :class:`bytearray`,        |                                       |
        | :class:`memoryview`        |                                       |
        +----------------------------+---------------------------------------+
        | :class:`datetime.datetime` | ISO8601 formatted timestamp in the    |
        |                            | extended format including separators, |
        |                            | milliseconds, and the timezone        |
        |                            | designator.                           |
        +----------------------------+---------------------------------------+
        | :class:`uuid.UUID`         | Same as ``str(value)``                |
        +----------------------------+---------------------------------------+

        .. warning::

           :class:`bytes` instances are treated as character strings by the
           standard JSON module in Python 2.7 so the *default* object hook
           is never called.  In other words, :class:`bytes` values will not
           be serialized as Base64 strings in Python 2.7.

        """
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        if isinstance(obj, (bytes, bytearray, memoryview)):
            return base64.b64encode(obj).decode('ASCII')
        raise TypeError('{!r} is not JSON serializable'.format(obj))
