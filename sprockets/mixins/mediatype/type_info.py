import array
import decimal
import ipaddress
import pathlib
import typing
import uuid

try:
    from typing import Protocol, runtime_checkable
except ImportError:
    # "ignore" is required to avoid an incompatible import
    # error due to different bindings of _SpecialForm
    from typing_extensions import Protocol, runtime_checkable  # type: ignore


@runtime_checkable
class SupportsDataclassFields(Protocol):
    """An object that looks like a dataclass.

    The implementation uses the same test that :func:`dataclasses.is_dataclass`
    uses in Python 3.9.

    """
    __dataclass_fields__: typing.ClassVar[typing.Mapping[str, typing.Any]]


@runtime_checkable
class SupportsIsoFormat(Protocol):
    """An object that has an isoformat method."""
    def isoformat(self) -> str:
        """Return the date/time in ISO-8601 format."""
        ...


class SupportsSettings(Protocol):
    """Something that quacks like a tornado.web.Application."""
    settings: typing.Dict[str, typing.Any]
    """Application settings."""


Serializable = typing.Union[SupportsIsoFormat, None, bool, bytearray, bytes,
                            float, int, memoryview, str, typing.Mapping,
                            typing.Sequence, typing.Set, uuid.UUID,
                            decimal.Decimal, SupportsDataclassFields,
                            ipaddress.IPv4Address, ipaddress.IPv6Address,
                            pathlib.Path, array.array]
"""Types that can be serialized by this library.

This is the set of types that
:meth:`sprockets.mixins.mediatype.content.ContentMixin.send_response`
is capable for serializing.

"""

Deserialized = typing.Union[None, bytes, typing.Mapping, float, int, list, str]
"""Possible result of deserializing a body.

This is the set of types that
:meth:`sprockets.mixins.mediatype.content.ContentMixin.get_request_body`
might return.

"""

PackBFunction = typing.Callable[[Serializable], bytes]
"""Signature of a binary content handler's serialization hook."""

UnpackBFunction = typing.Callable[[bytes], Deserialized]
"""Signature of a binary content handler's deserialization hook."""

DumpSFunction = typing.Callable[[Serializable], str]
"""Signature of a text content handler's serialization hook."""

LoadSFunction = typing.Callable[[str], Deserialized]
"""Signature of a text content handler's deserialization hook."""

MsgPackable = typing.Union[None, bool, bytes, typing.Dict[typing.Any,
                                                          typing.Any], float,
                           int, typing.List[typing.Any], str]
"""Set of types that the underlying msgpack library can serialize."""

JsonDumpable = typing.Union[None, bool, typing.Mapping[typing.Any, typing.Any],
                            float, int, typing.Sequence[typing.Any], str, None]
"""Set of types that the underlying msgpack library can serialize."""


class Transcoder(Protocol):
    """Object that transforms objects to bytes and back again.

    Transcoder instances are identified by their `content_type`
    instance attribute and registered by calling
    :func:`~sprockets.mixins.mediatype.content.add_transcoder`.
    They are used to implement request deserialization
    (:meth:`~sprockets.mixins.mediatype.content.ContentMixin.get_request_body`)
    and response body serialization
    (:meth:`~sprockets.mixins.mediatype.content.ContentMixin.send_response`)

    """
    content_type: str
    """Canonical content type that this transcoder implements."""
    def to_bytes(
            self,
            inst_data: Serializable,
            encoding: typing.Optional[str] = None) -> typing.Tuple[str, bytes]:
        """Serialize `inst_data` into a byte stream and content type spec.

        :param inst_data: the data to serialize
        :param encoding: optional encoding to use when serializing

        The content type is returned since it may contain the encoding
        or character set as a parameter.  The `encoding` parameter may
        not be used by all transcoders.

        :returns: tuple of the content type and the resulting bytes

        """
        ...

    def from_bytes(self,
                   data_bytes: bytes,
                   encoding: typing.Optional[str] = None) -> Deserialized:
        """Deserialize `bytes` into a Python object instance.

        :param data_bytes: byte string to deserialize
        :param encoding: optional encoding to use when deserializing

        The `encoding` parameter may not be used by all transcoders.

        :returns: the decoded Python object

        """
        ...
