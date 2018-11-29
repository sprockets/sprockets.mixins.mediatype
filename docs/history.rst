Version History
===============

`3.0.0`_ (1 Dec 2018)
---------------------
- Drop support for Python < 3.5
- Drop support for Tornado < 5.0
- Add :class:`sprockets.mixins.mediatype.transcoders.HTMLTranscoder`

`2.2.2`_ (7 Apr 2018)
---------------------
- Add support for Python 3.5 through 3.7
- Add support for Tornado < 6

`2.2.1`_ (12 Apr 2018)
----------------------
- Pin :mod:`ietfparse` to avoid breakages introduced in 1.5.0.

`2.2.0`_ (7 Jun 2017)
---------------------
- Add :func:`sprockets.mixins.mediatype.content.install`.
- Add :func:`sprockets.mixins.mediatype.content.get_settings`.
- Deprecate :meth:`sprockets.mixins.mediatype.content.ContentSettings.from_application`.
- Update to ietfparse 1.4.

`2.1.0`_ (16 Mar 2016)
----------------------
- Set the :http:header:`Vary` header if we are setting the content type.

`2.0.1`_ (29 Feb 2016)
----------------------
- Removed deprecation wrapper since it seems to cause really interesting
  problems including the much feared meta-class error.

`2.0.0`_ (24 Feb 2016)
----------------------
- Repackage from a module into a package.  Distributing raw modules inside
  of a namespace package is unreliable and questionably correct.
- Add :func:`sprockets.mixins.mediatype.content.add_transcoder`.
- Add :class:`sprockets.mixins.mediatype.transcoders.JSONTranscoder`.
- Add :class:`sprockets.mixins.mediatype.transcoders.MsgPackTranscoder`.
- Add :class:`sprockets.mixins.mediatype.transcoders.BinaryWrapper`.
- Normalize registered MIME types.
- Raise a 400 status when content body decoding fails.

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

.. _Next Release: https://github.com/sprockets/sprockets.mixins.media_type/compare/3.0.0...HEAD
.. _3.0.0: https://github.com/sprockets/sprockets.mixins.media_type/compare/2.2.2...3.0.0
.. _2.2.2: https://github.com/sprockets/sprockets.mixins.media_type/compare/2.2.1...2.2.2
.. _2.2.1: https://github.com/sprockets/sprockets.mixins.media_type/compare/2.2.0...2.2.1
.. _2.2.0: https://github.com/sprockets/sprockets.mixins.media_type/compare/2.1.0...2.2.0
.. _2.1.0: https://github.com/sprockets/sprockets.mixins.media_type/compare/2.0.1...2.1.0
.. _2.0.1: https://github.com/sprockets/sprockets.mixins.media_type/compare/2.0.0...2.0.1
.. _2.0.0: https://github.com/sprockets/sprockets.mixins.media_type/compare/1.0.4...2.0.0
.. _1.0.4: https://github.com/sprockets/sprockets.mixins.media_type/compare/1.0.3...1.0.4
.. _1.0.3: https://github.com/sprockets/sprockets.mixins.media_type/compare/1.0.2...1.0.3
.. _1.0.2: https://github.com/sprockets/sprockets.mixins.media_type/compare/1.0.1...1.0.2
.. _1.0.1: https://github.com/sprockets/sprockets.mixins.media_type/compare/1.0.0...1.0.1
.. _1.0.0: https://github.com/sprockets/sprockets.mixins.media_type/compare/0.0.0...1.0.0
