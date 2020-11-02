Version History
===============

`3.0.4`_ (2 Nov 2020)
---------------------
- Return a "400 Bad Request" when an invalid Content-Type header is received
  instead of failing with an internal server error

`3.0.3`_ (14 Sep 2020)
----------------------
- Import from collections.abc instead of collections (thanks @nullsvm)

`3.0.2`_ (4 May 2020)
---------------------
- Do not log tracebacks when decoding the request body fails

`3.0.1`_ (5 Mar 2019)
---------------------
- Set Tornado PIN to >=5, <7
- Remove setuptools_scm

`3.0.0`_ (4 Dec 2018)
---------------------
- Add MessagePack dependencies to package extras (eg. `pip install sprockets.mixins.mediatype[msgpack]`)
- Update to minimum of ietfparse 1.5.1
- Drop support for Python < 3.7
- Drop support for Tornado < 5
- Remove deprecated :meth:`sprockets.mixins.mediatype.content.ContentSettings.from_application`.

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

.. _Next Release: https://github.com/sprockets/sprockets.mixins.mediatype/compare/3.0.4...HEAD
.. _3.0.4: https://github.com/sprockets/sprockets.mixins.mediatype/compare/3.0.3...3.0.4
.. _3.0.3: https://github.com/sprockets/sprockets.mixins.mediatype/compare/3.0.2...3.0.3
.. _3.0.2: https://github.com/sprockets/sprockets.mixins.mediatype/compare/3.0.1...3.0.2
.. _3.0.1: https://github.com/sprockets/sprockets.mixins.mediatype/compare/3.0.0...3.0.1
.. _3.0.0: https://github.com/sprockets/sprockets.mixins.mediatype/compare/2.2.2...3.0.0
.. _2.2.2: https://github.com/sprockets/sprockets.mixins.mediatype/compare/2.2.1...2.2.2
.. _2.2.1: https://github.com/sprockets/sprockets.mixins.mediatype/compare/2.2.0...2.2.1
.. _2.2.0: https://github.com/sprockets/sprockets.mixins.mediatype/compare/2.1.0...2.2.0
.. _2.1.0: https://github.com/sprockets/sprockets.mixins.mediatype/compare/2.0.1...2.1.0
.. _2.0.1: https://github.com/sprockets/sprockets.mixins.mediatype/compare/2.0.0...2.0.1
.. _2.0.0: https://github.com/sprockets/sprockets.mixins.mediatype/compare/1.0.4...2.0.0
.. _1.0.4: https://github.com/sprockets/sprockets.mixins.mediatype/compare/1.0.3...1.0.4
.. _1.0.3: https://github.com/sprockets/sprockets.mixins.mediatype/compare/1.0.2...1.0.3
.. _1.0.2: https://github.com/sprockets/sprockets.mixins.mediatype/compare/1.0.1...1.0.2
.. _1.0.1: https://github.com/sprockets/sprockets.mixins.mediatype/compare/1.0.0...1.0.1
.. _1.0.0: https://github.com/sprockets/sprockets.mixins.mediatype/compare/0.0.0...1.0.0
