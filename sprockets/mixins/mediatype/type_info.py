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
    def isoformat(self) -> str:  # pragma: no cover
        ...


DeserializedPrimitives = Union[int, float, str, None]
DeserializedType = Union[DeserializedPrimitives,
                         Dict[str, Union[DeserializedPrimitives,
                                         Dict[str, Any], List[Any]]]]

SerializablePrimitives = Union[int, str, bytes, bytearray, memoryview,
                               ISOFormattable, uuid.UUID, None]
"""Non-collection types that this library knows how to serialize."""

SerializableTypes = Union[SerializablePrimitives, Mapping[str, Any],
                          Iterable[Any]]
"""Types that this library knows how to serialize."""

PackFunctionType = Callable[[SerializableTypes], bytes]
"""Function that packs a serializable instance to bytes."""

UnpackFunctionType = Callable[[bytes], DeserializedType]
"""Function that unpacks bytes into a object."""

DumpStringFunctionType = Callable[[SerializableTypes], str]
"""Function that packs a serializable instance to a string."""

LoadStringFunctionType = Callable[[str], DeserializedType]
"""Function that unpacks a object from a string."""


class ContentHandlerProtocol(Protocol):  # pragma: no cover
    content_type: str

    def to_bytes(self,
                 inst_data: SerializableTypes,
                 encoding: Optional[str] = None) -> Tuple[str, bytes]:
        ...

    def from_bytes(self,
                   data_bytes: bytes,
                   encoding: Optional[str] = None) -> DeserializedType:
        ...


class ApplicationProtocol(Protocol):  # quacks like web.Application
    settings: Dict[str, Any]
