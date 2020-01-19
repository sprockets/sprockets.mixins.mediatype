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

Type Information
----------------
.. module:: sprockets.mixins.mediatype.type_info

.. class:: ApplicationProtocol
.. class:: ContentHandlerProtocol
.. autodata:: DumpStringFunctionType
.. class:: ISOFormattable
.. autodata:: LoadStringFunctionType
.. autodata:: PackFunctionType
.. autodata:: SerializablePrimitives
.. autodata:: SerializableTypes
.. autodata:: UnpackFunctionType
