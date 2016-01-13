Version History
===============

`Next Release`_
---------------
- Repackage from a module into a package.  Distributing raw modules inside
  of a namespace package is unreliable and questionably correct.
- Add :func:`sprockets.mixins.mediatype.content.add_transcoder`.
- Add :class:`sprockets.mixins.mediatype.transcoders.JSONTranscoder`
- Add :class:`sprockets.mixins.mediatype.transcoders.MsgPackTranscoder`

`1.0.4`_ (14 Sep 2015)
----------------------
- Support using the default_content_type in the settings if request does not
  contain the Accept header

`1.0.3`_ (10 Sep 2015)
----------------------
- Update installation files

`1.0.2`_ (9 Sep 2015)
---------------------
- Rename package to mediatype

`1.0.1`_ (9 Sep 2015)
---------------------
- Repackaged for Travis-CI configuration.

`1.0.0`_ (9 Sep 2015)
---------------------
- Initial Release

.. _Next Release: https://github.com/sprockets/sprockets.http/compare/1.0.4...HEAD
.. _1.0.4: https://github.com/sprockets/sprockets.http/compare/1.0.3...1.0.4
.. _1.0.3: https://github.com/sprockets/sprockets.http/compare/1.0.2...1.0.3
.. _1.0.2: https://github.com/sprockets/sprockets.http/compare/1.0.1...1.0.2
.. _1.0.1: https://github.com/sprockets/sprockets.http/compare/1.0.0...1.0.1
.. _1.0.0: https://github.com/sprockets/sprockets.http/compare/0.0.0...1.0.0
