"""
Bundled media type transcoders.

- :class:`.JSONTranscoder` implements JSON encoding/decoding
- :class:`.MsgPackTranscoder` implements msgpack encoding/decoding
- :class:`.FormUrlEncodedTranscoder` implements the venerable form encoding

"""
from __future__ import annotations

import base64
import dataclasses
import json
import string
import typing
import urllib.parse
import uuid

import collections.abc

try:
    import umsgpack
except ImportError:  # pragma: no cover
    umsgpack = None  # type: ignore

from sprockets.mixins.mediatype import handlers, type_info

_FORM_URLENCODING = {c: '%{:02X}'.format(c) for c in range(0, 255)}
_FORM_URLENCODING.update({ord(c): c for c in string.ascii_letters})
_FORM_URLENCODING.update({ord(c): c for c in string.digits})
_FORM_URLENCODING.update({ord(c): c for c in '*-_.'})

_FORM_URLENCODING_PLUS = _FORM_URLENCODING.copy()
_FORM_URLENCODING_PLUS[ord(' ')] = '+'


class JSONTranscoder(handlers.TextContentHandler):
    """
    JSON transcoder instance.

    :param content_type: the content type that this encoder instance
        implements. If omitted, ``application/json`` is used. This is
        passed directly to the ``TextContentHandler`` initializer.
    :param default_encoding: the encoding to use if none is specified.
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
    dump_options: typing.Dict[str, typing.Any]
    load_options: typing.Dict[str, typing.Any]

    def __init__(self,
                 content_type: str = 'application/json',
                 default_encoding: str = 'utf-8') -> None:
        super().__init__(content_type, self.dumps, self.loads,
                         default_encoding)
        self.dump_options = {
            'default': self.dump_object,
            'separators': (',', ':'),
        }
        self.load_options = {}

    def dumps(self, obj: type_info.Serializable) -> str:
        """Dump a :class:`object` instance into a JSON :class:`str`"""
        return json.dumps(obj, **self.dump_options)

    def loads(self, str_repr: str) -> type_info.Deserialized:
        """Transform :class:`str` into an :class:`object` instance."""
        return typing.cast(type_info.Deserialized,
                           json.loads(str_repr, **self.load_options))

    def dump_object(self, obj: type_info.Serializable) -> str:
        """
        Called to encode unrecognized object.

        :param obj: the object to encode
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

        """
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if hasattr(obj, 'isoformat'):
            return typing.cast(type_info.DefinesIsoFormat, obj).isoformat()
        if isinstance(obj, (bytes, bytearray, memoryview)):
            return base64.b64encode(obj).decode('ASCII')
        raise TypeError('{!r} is not JSON serializable'.format(obj))


class MsgPackTranscoder(handlers.BinaryContentHandler):
    """
    Msgpack Transcoder instance.

    :param content_type: the content type that this encoder instance
        implements. If omitted, ``application/msgpack`` is used. This
        is passed directly to the ``BinaryContentHandler`` initializer.

    This transcoder uses the `umsgpack`_ library to encode and decode
    objects according to the `msgpack format`_.

    .. _umsgpack: https://github.com/vsergeev/u-msgpack-python
    .. _msgpack format: http://msgpack.org/index.html

    """
    PACKABLE_TYPES = (bool, int, float)

    def __init__(self, content_type: str = 'application/msgpack') -> None:
        if umsgpack is None:
            raise RuntimeError('Cannot import MsgPackTranscoder, '
                               'umsgpack is not available')

        super().__init__(content_type, self.packb, self.unpackb)

    def packb(self, data: type_info.Serializable) -> bytes:
        """Pack `data` into a :class:`bytes` instance."""
        return umsgpack.packb(self.normalize_datum(data))

    def unpackb(self, data: bytes) -> type_info.Deserialized:
        """Unpack a :class:`object` from a :class:`bytes` instance."""
        return umsgpack.unpackb(data)

    def normalize_datum(
            self, datum: type_info.Serializable) -> type_info.MsgPackable:
        """
        Convert `datum` into something that umsgpack likes.

        :param datum: something that we want to process with umsgpack
        :return: a packable version of `datum`
        :raises TypeError: if `datum` cannot be packed

        This message is called by :meth:`.packb` to recursively normalize
        an input value before passing it to :func:`umsgpack.packb`.  Values
        are normalized according to the following table.

        +-----------------------------------+-------------------------------+
        | **Value**                         | **MsgPack Family**            |
        +-----------------------------------+-------------------------------+
        | :data:`None`                      | `nil byte`_ (0xC0)            |
        +-----------------------------------+-------------------------------+
        | :data:`True`                      | `true byte`_ (0xC3)           |
        +-----------------------------------+-------------------------------+
        | :data:`False`                     | `false byte`_ (0xC2)          |
        +-----------------------------------+-------------------------------+
        | :class:`int`                      | `integer family`_             |
        +-----------------------------------+-------------------------------+
        | :class:`float`                    | `float family`_               |
        +-----------------------------------+-------------------------------+
        | String                            | `str family`_                 |
        +-----------------------------------+-------------------------------+
        | :class:`bytes`                    | `bin family`_                 |
        +-----------------------------------+-------------------------------+
        | :class:`bytearray`                | `bin family`_                 |
        +-----------------------------------+-------------------------------+
        | :class:`memoryview`               | `bin family`_                 |
        +-----------------------------------+-------------------------------+
        | :class:`collections.abc.Sequence` | `array family`_               |
        +-----------------------------------+-------------------------------+
        | :class:`collections.abc.Set`      | `array family`_               |
        +-----------------------------------+-------------------------------+
        | :class:`collections.abc.Mapping`  | `map family`_                 |
        +-----------------------------------+-------------------------------+
        | :class:`uuid.UUID`                | Converted to String           |
        +-----------------------------------+-------------------------------+

        .. _nil byte: https://github.com/msgpack/msgpack/blob/
           0b8f5ac67cdd130f4d4d4fe6afb839b989fdb86a/spec.md#formats-nil
        .. _true byte: https://github.com/msgpack/msgpack/blob/
           0b8f5ac67cdd130f4d4d4fe6afb839b989fdb86a/spec.md#bool-format-family
        .. _false byte: https://github.com/msgpack/msgpack/blob/
           0b8f5ac67cdd130f4d4d4fe6afb839b989fdb86a/spec.md#bool-format-family
        .. _integer family: https://github.com/msgpack/msgpack/blob/
           0b8f5ac67cdd130f4d4d4fe6afb839b989fdb86a/spec.md#int-format-family
        .. _float family: https://github.com/msgpack/msgpack/blob/
           0b8f5ac67cdd130f4d4d4fe6afb839b989fdb86a/spec.md#float-format-family
        .. _str family: https://github.com/msgpack/msgpack/blob/
           0b8f5ac67cdd130f4d4d4fe6afb839b989fdb86a/spec.md#str-format-family
        .. _array family: https://github.com/msgpack/msgpack/blob/
           0b8f5ac67cdd130f4d4d4fe6afb839b989fdb86a/spec.md#array-format-family
        .. _map family: https://github.com/msgpack/msgpack/blob/
           0b8f5ac67cdd130f4d4d4fe6afb839b989fdb86a/spec.md
           #mapping-format-family
        .. _bin family: https://github.com/msgpack/msgpack/blob/
           0b8f5ac67cdd130f4d4d4fe6afb839b989fdb86a/spec.md#bin-format-family

        """
        if datum is None:
            return datum

        if isinstance(datum, self.PACKABLE_TYPES):
            return datum

        if isinstance(datum, uuid.UUID):
            datum = str(datum)

        if isinstance(datum, bytearray):
            datum = bytes(datum)

        if isinstance(datum, memoryview):
            datum = datum.tobytes()

        if hasattr(datum, 'isoformat'):
            datum = typing.cast(type_info.DefinesIsoFormat, datum).isoformat()

        if isinstance(datum, (bytes, str)):
            return datum

        if isinstance(datum, (collections.abc.Sequence, collections.abc.Set)):
            return [self.normalize_datum(item) for item in datum]

        if isinstance(datum, collections.abc.Mapping):
            out = {}
            for k, v in datum.items():
                out[k] = self.normalize_datum(v)
            return out

        raise TypeError('{} is not msgpackable'.format(
            datum.__class__.__name__))


@dataclasses.dataclass
class FormUrlEncodingOptions:
    """Configuration knobs for :class:`.FormUrlEncodedTranscoder`"""
    encoding: str = 'utf-8'
    """Encoding use when generating the byte stream from character data."""

    literal_mapping: dict[typing.Literal[None, True, False],
                          str] = dataclasses.field(default_factory=lambda: {
                              None: '',
                              True: 'true',
                              False: 'false'
                          })
    """Mapping from supported literal values to strings."""

    space_as_plus: bool = False
    """Quote spaces as ``%20`` or ``+``."""


class FormUrlEncodedTranscoder:
    """Opinionated transcoder for the venerable x-www-formurlencoded.

    This transcoder implements transcoding according to the current
    W3C documentation.

    * character strings are encoded as UTF-8 codepoints before
      percent-encoding the resulting bytes
    * the space character is represented as ``%20``
    * :data:`False` is represented as ``false``
    * :data:`True` is represented as ``true``
    * :data:`None` is represented as the empty string

    Some of the opinions can be changed by modifying ``self.options``.

    https://url.spec.whatwg.org/#application/x-www-form-urlencoded

    .. attribute:: options
       :type: FormUrlEncodingOptions

       Controls the behavior of the transcoder

    """
    content_type = 'application/x-www-formurlencoded'

    def __init__(self) -> None:
        self.options = FormUrlEncodingOptions()

    def to_bytes(
            self,
            inst_data: type_info.Serializable,
            encoding: typing.Optional[str] = None) -> typing.Tuple[str, bytes]:
        """Serialize `inst_data` into a byte stream and content type spec.

        :param inst_data: the data to serialize
        :param encoding: optional encoding override

        Serialization is implemented as described in the W3C
        `urlencoded serialization`_ algorithm.  The :attr:`.options`
        attribute controls the configurable details of the encoding
        process.

        The character encoding can be further overridden by specifying the
        `encoding` parameter.

        :returns: tuple of the content type and the resulting bytes
        :raises: :exc:`TypeError` if a supplied value cannot be serialized

        .. _urlencoded serialization: https://url.spec.whatwg.org/
           #urlencoded-serializing

        """
        # Select the appropriate encoding table and use the default
        # character encoding if necessary.  Binding these to locals
        # removes branches from the inner loop.
        chr_map: typing.Mapping[int, str]
        chr_map = (_FORM_URLENCODING_PLUS
                   if self.options.space_as_plus else _FORM_URLENCODING)
        if encoding is None:
            encoding = self.options.encoding

        # Generate a sequence of name+value tuples to encode
        if isinstance(inst_data, type_info.SerializablePrimitives):
            encoded = self._encode(inst_data, chr_map, encoding)
            return self.content_type, encoded.encode('ascii')

        if isinstance(inst_data, collections.abc.Mapping):
            tuples = inst_data.items()
        else:
            tuples = inst_data

        # Encode each pair and run the encoded form through the
        # appropriate octet to string mapping table
        prefix = ''  # micro-optimization removes if statement from inner loop
        buf = []
        for name, value in tuples:
            buf.append(prefix)
            buf.extend(self._encode(name, chr_map, encoding))
            buf.append('=')
            buf.extend(self._encode(value, chr_map, encoding))
            prefix = '&'

        return self.content_type, ''.join(buf).encode('ascii')

    def from_bytes(
            self,
            data_bytes: bytes,
            encoding: typing.Optional[str] = None) -> type_info.Deserialized:
        """Deserialize `bytes` into a Python object instance.

        :param data_bytes: byte string to deserialize
        :param encoding: optional encoding override

        Deserialization is implemented according to the W3C
        `urlencoded deserialization`_ algorithm.  The :attr:`.options`
        attribute controls the configurable details of the encoding
        process.

        :returns: the decoded Python object

        .. _urlencoded deserialization: https://url.spec.whatwg.org/
           #urlencoded-parsing

        """
        dequote = (urllib.parse.unquote_plus
                   if self.options.space_as_plus else urllib.parse.unquote)
        if encoding is None:
            encoding = self.options.encoding

        output = []
        for part in data_bytes.decode('ascii').split('&'):
            if not part:
                continue
            name, eq_present, value = part.partition('=')
            name = dequote(name, encoding=encoding)
            if eq_present:
                output.append((name, dequote(value, encoding=encoding)))
            else:
                output.append((name, ''))

        return dict(output)

    def _encode(self, datum: typing.Union[bool, None, float, int, str,
                                          type_info.DefinesIsoFormat],
                char_map: typing.Mapping[int, str], encoding: str) -> str:
        try:
            datum = self.options.literal_mapping[datum]  # type: ignore
        except (KeyError, TypeError):
            if isinstance(datum, (float, int, str)):
                datum = str(datum)
            elif hasattr(datum, 'isoformat'):
                datum = datum.isoformat()
            elif isinstance(datum, (bytearray, bytes, memoryview)):
                return ''.join(char_map[c] for c in datum)
            else:
                raise TypeError(
                    f'{datum.__class__.__name__} is not serializable'
                ) from None

        return ''.join(char_map[c] for c in datum.encode(encoding))
