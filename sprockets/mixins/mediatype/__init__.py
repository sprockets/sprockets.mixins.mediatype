"""
sprockets.mixins.mediatype

"""
import typing

try:
    from .content import (ContentMixin, ContentSettings,
                          add_binary_content_type, add_text_content_type,
                          set_default_content_type)
except ImportError as error:  # noqa: F841  # pragma no cover

    def _error_closure(*args, **kwargs):  # type: ignore
        raise error  # noqa: F821

    class ErrorClosureClass(object):
        def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
            raise error  # noqa: F821

    ContentMixin = ErrorClosureClass  # type: ignore
    ContentSettings = ErrorClosureClass  # type: ignore
    add_binary_content_type = _error_closure
    add_text_content_type = _error_closure
    set_default_content_type = _error_closure

version_info = (3, 0, 1)
__version__ = '.'.join(str(x) for x in version_info)

__all__ = [
    'ContentMixin', 'ContentSettings', 'add_binary_content_type',
    'add_text_content_type', 'set_default_content_type', 'version_info',
    '__version__'
]
