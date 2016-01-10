"""Bundled media type transcoders."""
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

    .. attribute:: dump_options

       Keyword parameters that are passed to :func:`json.dumps` when
       :meth:`.dumps` is called.

    .. attribute:: load_options

       Keyword parameters that are passed to :func:`json.loads` when
       :meth:`.loads` is called.

    """

    def __init__(self, content_type='application/json',
                 default_encoding='utf-8'):
        super(JSONTranscoder, self).__init__(content_type, self.dumps,
                                             self.loads, default_encoding)
        self.dump_options = {}
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
