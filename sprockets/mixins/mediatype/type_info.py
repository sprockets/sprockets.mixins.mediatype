import sys
from typing import (Any, Callable, Dict, Iterable, List, Mapping, Optional,
                    Tuple, Union)
import uuid

if sys.version_info[:2] >= (3, 8):  # pragma: no cover
    from typing import Literal, Protocol
else:  # pragma: no cover
    from typing_extensions import Literal, Protocol

__all__ = [
    'ApplicationProtocol',
    'ContentHandlerProtocol',
    'DeserializedPrimitives',
    'DeserializedType',
    'DumpStringFunctionType',
    'ISOFormattable',
    'LoadStringFunctionType',
    'PackFunctionType',
    'SerializablePrimitives',
    'SerializableTypes',
    'UnpackFunctionType',

    # The following are exported to support Python 3.7
    'Literal',
    'Protocol',
]


class ISOFormattable(Protocol):
    """Protocol for things that look like a datetime.

    Instances that match this protocol will be serialized as the
    string value returned from the :meth:`isoformat` method.

    """
    def isoformat(self) -> str:  # pragma: no cover
        """Format as a ISO-8601 value.

        :rtype: str

        """
        ...


DeserializedPrimitives = Union[bool, float, int, str, None]
"""Primitive types that are returned from deserialization functions."""

DeserializedType = Union[DeserializedPrimitives,
                         Dict[str, Union[DeserializedPrimitives,
                                         Dict[str, Any], List[Any]]],
                         List[Union[DeserializedPrimitives, Dict[str, Any],
                                    List[Any]]]]
"""Deserializable types.

This type specifies the result of deserializing a byte stream or
string.  This is NOT the inverse of :data:`SerializableTypes` since
deserialization functions do not interpret primitive strings into
more complex values like dates or UUIDs.

+-----------------------+-------------------+
| integer value         | :class:`int`      |
+-----------------------+-------------------+
| floating point value  | :class:`float`    |
+-----------------------+-------------------+
| string value          | :class:`str`      |
+-----------------------+-------------------+
| "null" value          | :data:`None`      |
+-----------------------+-------------------+
| Boolean value         | :class:`bool`     |
+-----------------------+-------------------+
| mapping               | :class:`dict`     |
+-----------------------+-------------------+
| sequence              | :class:`list`     |
+-----------------------+-------------------+

"""

SerializablePrimitives = Union[int, str, bytes, bytearray, memoryview,
                               ISOFormattable, uuid.UUID, None]
"""Non-collection types that this library knows how to serialize."""

SerializableTypes = Union[SerializablePrimitives, Mapping[str, Any],
                          Iterable[Any]]
"""Serializable types.

+------------------------------------+---------------------------------------+
| :class:`bool`                      | Boolean value                         |
+------------------------------------+---------------------------------------+
| :class:`int`                       | numeric value                         |
+------------------------------------+---------------------------------------+
| :class:`float`                     | numeric value                         |
+------------------------------------+---------------------------------------+
| :class:`str`                       | string value                          |
+------------------------------------+---------------------------------------+
| :class:`bytes`                     | binary if supported, base64 otherwise |
+------------------------------------+---------------------------------------+
| :class:`datetime.datetime`         | ISO-8601 formatted timestamp          |
+------------------------------------+---------------------------------------+
| :class:`uuid.UUID`                 | stringified                           |
+------------------------------------+---------------------------------------+
| :data:`None`                       | "null" value                          |
+------------------------------------+---------------------------------------+
| :class:`collections.abc.Mapping`   | recursively serialized                |
+------------------------------------+---------------------------------------+
| :class:`collections.abc.Iterable`  | recursively serialized as list        |
+------------------------------------+---------------------------------------+

"""

PackFunctionType = Callable[[SerializableTypes], bytes]
"""Function that packs a serializable instance to bytes.

:param SerializableTypes o: instance to serialize
:returns: the byte string serialization of `o`
:rtype: bytes

See :data:`SerializableTypes` for how various types are serialized.

"""

UnpackFunctionType = Callable[[bytes], DeserializedType]
"""Function that unpacks bytes into a object.

:param bytes data: byte string to unpack
:returns: the deserialized instance
:rtype: DeserializedType

See :data:`DeserializedType` for how various types are deserialized.

"""

DumpStringFunctionType = Callable[[SerializableTypes], str]
"""Function that renders a serializable instance as a string.

:param SerializableTypes o: instance to serialize
:returns: the string serialization of `o`
:rtype: str

See :data:`SerializableTypes` for how various types are serialized.

"""

LoadStringFunctionType = Callable[[str], DeserializedType]
"""Function that parses a object from a string.

:param str data: string to parse
:returns: the deserialized instance
:rtype: DeserializedType

See :data:`DeserializedType` for how various types are deserialized.

"""


class ContentHandlerProtocol(Protocol):  # pragma: no cover
    """Transforms between support serializable types and bytes.

    This protocol describes what a content transcoder looks like.

    """

    content_type: str
    """:http:header:`Content-Type` that this serializer implements."""
    def to_bytes(self,
                 inst_data: SerializableTypes,
                 encoding: Optional[str] = None) -> Tuple[str, bytes]:
        """Transform an instance to a byte string.

        :param SerializableTypes inst_data: data value to serialized
        :param Optional[str] encoding: optional encoding to serialize
            `inst_data` with.
        :returns: the selected content type and the serialized data
        :rtype: Tuple[str, bytes]

        """
        ...

    def from_bytes(self,
                   data_bytes: bytes,
                   encoding: Optional[str] = None) -> DeserializedType:
        """Deserialized a byte string into a Python instance.

        :param bytes data_bytes: byte string to deserialize
        :param Optional[str] encoding: string encoding to use when
            deserializing.  If unspecified, a transcoder-specific
            encoding will be used.
        :rtype: DeserializedType

        """
        ...


class ApplicationProtocol(Protocol):  # quacks like web.Application
    """Protocol that an application MUST provide.

    This protocol describes the precise requirements that the application
    object is required to implement.  The :class:`tornado.web.Application`
    class implements this protocol.

    """
    settings: Dict[str, Any]
    """Application configuration dictionary."""
