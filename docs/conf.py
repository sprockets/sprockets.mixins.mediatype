import os

import pkg_resources

needs_sphinx = '4.0'
extensions = ['sphinx.ext.viewcode', 'sphinxcontrib.httpdomain']
master_doc = 'index'
project = 'sprockets.mixins.mediatype'
copyright = '2015-2021, AWeber Communications'
release = pkg_resources.get_distribution('sprockets.mixins.mediatype').version
version = '.'.join(release.split('.')[0:1])

# Only install the ReadTheDocs theme when we are not running
# in the RTD build system.
if not os.environ.get('READTHEDOCS', None):
    import sphinx_rtd_theme
    html_theme = 'sphinx_rtd_theme'
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

html_sidebars = {
    '**': ['about.html', 'navigation.html'],
}

# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html
extensions.append('sphinx.ext.intersphinx')
intersphinx_mapping = {
    'ietfparse': ('https://ietfparse.readthedocs.io/en/latest', None),
    'python': ('https://docs.python.org/3', None),
    'requests': ('https://requests.readthedocs.org/en/latest/', None),
    'sprockets': ('https://sprockets.readthedocs.org/en/latest/', None),
    'tornado': ('https://www.tornadoweb.org/en/stable/', None),
}

# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
# We need to define type aliases for both the simple name (e.g., Deserialized)
# and the prefixed name (e.g., type_info.Deserialized) since both forms
# appear in the typing annotations.
extensions.append('sphinx.ext.autodoc')
_names = {
    'Deserialized', 'DumpSFunction', 'LoadSFunction', 'MsgPackable',
    'PackBFunction', 'Serializable', 'SupportsIsoFormat', 'SupportsSettings',
    'Transcoder', 'UnpackBFunction'
}
autodoc_type_aliases = {
    alias: f'sprockets.mixins.mediatype.type_info.{alias}'
    for alias in _names
}
autodoc_type_aliases.update({
    f'type_info.{alias}': f'sprockets.mixins.mediatype.type_info.{alias}'
    for alias in _names
})

# https://www.sphinx-doc.org/en/master/usage/extensions/extlinks.html
extensions.append('sphinx.ext.extlinks')
extlinks = {
    'compare': ('https://github.com/sprockets/sprockets.mixins.mediatype'
                '/compare/%s', '%s')
}
