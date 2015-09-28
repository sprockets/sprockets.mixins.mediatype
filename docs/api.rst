API Documentation
=================

Content Type Handling
---------------------
.. autoclass:: sprockets.mixins.mediatype.ContentMixin
   :members:

Content Type Registration
-------------------------
.. autofunction:: sprockets.mixins.mediatype.set_default_content_type

.. autofunction:: sprockets.mixins.mediatype.add_binary_content_type

.. autofunction:: sprockets.mixins.mediatype.add_text_content_type

.. autoclass:: sprockets.mixins.mediatype.ContentSettings
   :members:

Content Type Transcoding
------------------------
The API supports instance-based transcoders in addition to the more common
function-based ones (e.g., :class:`json.JSONEncoder` instead of
:func:`json.dumps`).  Transcoders are simple classes that implement two
functions -- one to go from :class:`bytes` to :class:`object` and another
to go from :class:`object` to :class:`bytes`.

 .. method:: transcoder.to_bytes(self, data, encoding) -> bytes

    :param object data: object to encode
    :param str encoding: character encoding to apply or :data:`None`
    :returns: :class:`tuple` of the selected content type and the
        encoded :class:`bytes` instance

 .. method:: transcoder.from_bytes(self, data, encoding) -> object

    :param bytes data: byte stream to decode object from
    :param str encoding: character encoding to apply or :data:`None`
    :returns: decoded :class:`object` instance

The :mod:`sprockets.mixins.mediatype.transcoders` module provides a few
useful implementations that can be used as a basis for writing your own
custom transcoders.

-----

.. autofunction:: sprockets.mixins.mediatype.add_transcoder

.. autoclass:: sprockets.mixins.mediatype.transcoders.BinaryContentHandler
   :members:

.. autoclass:: sprockets.mixins.mediatype.transcoders.TextContentHandler
   :members:

.. autoclass:: sprockets.mixins.mediatype.transcoders.JSONTranscoder
   :members:

.. autoclass:: sprockets.mixins.mediatype.transcoders.MsgPackTranscoder
   :members:
