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

html_style = 'custom.css'
html_static_path = ['static']
html_sidebars = {
    '**': ['about.html', 'navigation.html'],
}
html_theme_options = {
    'github_user': 'sprockets',
    'github_repo': 'sprockets.mixins.mediatype',
    'description': 'Content-Type negotation mix-in',
    'github_banner': True,
    'sidebar_width': '230px',
}

# https://github.com/agronholm/sphinx-autodoc-typehints
extensions.append('sphinx_autodoc_typehints')
autodoc_type_hints = 'none'

intersphinx_mapping = {
    'ietfparse': ('https://ietfparse.readthedocs.io/en/latest/', None),
    'python': ('https://docs.python.org/3', None),
    'requests': ('https://requests.readthedocs.io/en/latest/', None),
    'sprockets': ('https://sprockets.readthedocs.io/en/latest/', None),
    'tornado': ('https://www.tornadoweb.org/en/latest/', None),
}
