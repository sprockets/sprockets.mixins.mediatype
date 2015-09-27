"""
Content transcoding classes & functions.

The :class:`sprockets.mixins.mediatype.ContentMixin` uses transcoder
instances *under the hood*.  A transcoder is responsible for transforming
objects to and from the :class:`bytes` instances held in a request body.
This module implements the transcoders.

"""
from tornado import escape


class BinaryContentHandler(object):

    def __init__(self, content_type, pack, unpack):
        self._pack = pack
        self._unpack = unpack
        self.content_type = content_type

    def to_bytes(self, data_dict, encoding=None):
        return self.content_type, self._pack(data_dict)

    def from_bytes(self, data, encoding=None):
        return self._unpack(data)


class TextContentHandler(object):

    def __init__(self, content_type, dumps, loads, default_encoding):
        self._dumps = dumps
        self._loads = loads
        self.content_type = content_type
        self.default_encoding = default_encoding

    def to_bytes(self, data_dict, encoding=None):
        selected = encoding or self.default_encoding
        content_type = '{}; charset="{}"'.format(self.content_type, selected)
        dumped = self._dumps(escape.recursive_unicode(data_dict))
        return content_type, dumped.encode(selected)

    def from_bytes(self, data, encoding=None):
        return self._loads(data.decode(encoding or self.default_encoding))
