"""
sprockets.mixins.mediatype

"""
try:
    from .content import (ContentMixin, ContentSettings,
                          add_binary_content_type, add_text_content_type,
                          set_default_content_type)
except ImportError as error:  # noqa: F841  # pragma no cover
    def _error_closure(*args, **kwargs):
        raise error  # noqa: F821

    class ErrorClosureClass(object):
        def __init__(self, *args, **kwargs):
            raise error  # noqa: F821

    ContentMixin = ErrorClosureClass
    ContentSettings = ErrorClosureClass
    add_binary_content_type = _error_closure
    add_text_content_type = _error_closure
    set_default_content_type = _error_closure


version_info = (3, 0, 4)
__version__ = '.'.join(str(x) for x in version_info)

__all__ = ['ContentMixin', 'ContentSettings', 'add_binary_content_type',
           'add_text_content_type', 'set_default_content_type',
           'version_info', '__version__']
