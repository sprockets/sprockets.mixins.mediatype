import pkg_resources

needs_sphinx = '1.0'
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinxcontrib.autohttp.tornado',
]
master_doc = 'index'
project = 'sprockets.mixins.mediatype'
copyright = '2015-2018, AWeber Communications'
release = pkg_resources.get_distribution('sprockets.mixins.mediatype').version
version = '.'.join(release.split('.')[0:1])

html_static_path = ['_static']
html_css_files = ['css/custom.css']
html_theme = 'sphinx_rtd_theme'
html_theme_options = {}

# https://github.com/agronholm/sphinx-autodoc-typehints
extensions.append('sphinx_autodoc_typehints')

intersphinx_mapping = {
    'ietfparse': ('https://ietfparse.readthedocs.io/en/latest/', None),
    'python': ('https://docs.python.org/3', None),
    'requests': ('https://requests.readthedocs.io/en/latest/', None),
    'sprockets': ('https://sprockets.readthedocs.io/en/latest/', None),
    'tornado': ('https://www.tornadoweb.org/en/latest/', None),
}
