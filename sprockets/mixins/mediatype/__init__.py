"""
sprockets.mixins.media_type

"""
import functools
import warnings

try:
    from .content import (ContentMixin, ContentSettings,
                          add_binary_content_type, add_text_content_type,
                          set_default_content_type)

except ImportError as error:  # pragma no cover
    def _error_closure(*args, **kwargs):
        raise error

    ContentMixin = _error_closure
    ContentSettings = _error_closure
    add_binary_content_type = _error_closure
    add_text_content_type = _error_closure
    set_default_content_type = _error_closure


def _mark_deprecated(func):
    msg = '{0}.{1} is deprecated, use {0}.content.{1} instead'.format(
        'sprockets.mixins.mediatype', func.__name__)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        warnings.warn(msg, category=DeprecationWarning)
        return func(*args, **kwargs)

    return wrapper

add_binary_content_type = _mark_deprecated(add_binary_content_type)
add_text_content_type = _mark_deprecated(add_text_content_type)
set_default_content_type = _mark_deprecated(set_default_content_type)
ContentMixin = _mark_deprecated(ContentMixin)
ContentSettings = _mark_deprecated(ContentSettings)

version_info = (2, 0, 0)
__version__ = '.'.join(str(v) for v in version_info)
__all__ = ('ContentMixin', 'ContentSettings', 'add_binary_content_type',
           'add_text_content_type', 'set_default_content_type',
           'version_info', '__version__')
