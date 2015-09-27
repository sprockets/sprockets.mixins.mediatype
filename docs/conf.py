import alabaster
from sprockets.mixins.mediatype import __version__

needs_sphinx = '1.0'
extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.viewcode',
              'sphinx.ext.intersphinx',
              'sphinxcontrib.autohttp.tornado']
source_suffix = '.rst'
master_doc = 'index'
project = 'sprockets.mixins.mediatype'
copyright = '2015, AWeber Communications'
release = __version__
version = '.'.join(release.split('.')[0:1])

pygments_style = 'sphinx'
html_theme = 'alabaster'
html_style = 'custom.css'
html_static_path = ['static']
html_theme_path = [alabaster.get_path()]
html_sidebars = {
    '**': ['about.html', 'navigation.html'],
}
html_theme_options = {
    'github_user': 'sprockets',
    'github_repo': 'sprockets.mixins.media_type',
    'description': 'Content-Type negotation mix-in',
    'github_banner': True,
    'travis_button': True,
    'sidebar_width': '230px',
}

intersphinx_mapping = {
    'ietfparse': ('https://ietfparse.readthedocs.org/en/latest', None),
    'python': ('https://docs.python.org/3', None),
    'requests': ('https://requests.readthedocs.org/en/latest/', None),
    'tornado': ('http://tornadoweb.org/en/latest/', None),
}
