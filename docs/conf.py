from sprockets.mixins.media_type import __version__

needs_sphinx = '1.0'
extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.viewcode',
              'sphinx.ext.intersphinx']
source_suffix = '.rst'
master_doc = 'index'
project = 'sprockets.mixins.media_type'
copyright = '2015, AWeber Communications'
release = __version__
version = '.'.join(release.split('.')[0:1])

intersphinx_mapping = {
    'python': ('https://docs.python.org/', None),
    'requests': ('https://requests.readthedocs.org/en/latest/', None),
    'sprockets': ('https://sprockets.readthedocs.org/en/latest/', None),
}
