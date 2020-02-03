API Documentation
=================
.. currentmodule:: sprockets.mixins.mediatype.content

Content Type Handling
---------------------
.. autodata:: SETTINGS_KEY

.. autoclass:: ContentMixin
   :members:

Content Type Registration
-------------------------
.. autofunction:: install

.. autofunction:: get_settings

.. autofunction:: set_default_content_type

.. autofunction:: add_binary_content_type

.. autofunction:: add_text_content_type

.. autofunction:: add_transcoder

.. autoclass:: ContentSettings
   :members:

Bundled Transcoders
-------------------
.. currentmodule:: sprockets.mixins.mediatype.transcoders

.. autoclass:: JSONTranscoder
   :members:

.. autoclass:: MsgPackTranscoder
   :members:

Low-level Interfaces
--------------------
.. currentmodule:: sprockets.mixins.mediatype.handlers

.. autoclass:: BinaryContentHandler
   :members:

.. autoclass:: TextContentHandler
   :members:

Type Information
----------------
.. module:: sprockets.mixins.mediatype.type_info

This module provides precise types for this library as described in :pep:`484`.
Since :mod:`typing` based type definitions are parsed as "data" objects, the
documentation styling may not match your expectations.  The types fall into
several different categories:

Protocols that describe expectations
   - :class:`ApplicationProtocol` describes things that are treated as
     :class:`tornado.web.Application` instances
   - :class:`ISOFormattable` describes things that are treated as
     :class:`datetime.datetime` instances
   - :class:`ContentHandlerProtocol` describes how a plugable content
     handler behaves

Constraints on functions
   - :data:`DumpStringFunctionType` and :data:`LoadStringFunctionType`
     describe functions that translate between strings and Python instances
   - :data:`PackFunctionType` and :data:`UnpackFunctionType` describe functions
     that translate between byte streams and Python instances

Sets of types used to constrain parameters and return values
   - :data:`SerializableTypes` and :data:`SerializablePrimitives` describe
     what python instances are serialized into
   - :data:`DeserializedType` and :data:`DeserializedPrimitives` describe
     what to expect when deserializing a stream

.. autoclass:: ApplicationProtocol
   :members:

.. autoclass:: ContentHandlerProtocol
   :members:

.. autoclass:: ISOFormattable
   :members:

.. autodata:: DumpStringFunctionType
   :annotation: (s: str) -> DeserializedType

.. autodata:: LoadStringFunctionType
   :annotation: (o: SerializableTypes) -> str

.. autodata:: PackFunctionType
   :annotation: (o: SerializableTypes) -> bytes

.. autodata:: SerializablePrimitives
   :annotation:

.. autodata:: SerializableTypes
   :annotation:

.. autodata:: UnpackFunctionType
   :annotation: (data: bytes) -> DeserializedType

.. autodata:: DeserializedType
   :annotation:

.. autodata:: DeserializedPrimitives
   :annotation:
