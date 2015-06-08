sprockets.mixins.media_type
===========================
A mixin that performs Content-Type negotiation and request/response (de)serialization.

|Version| |Downloads| |Status| |Coverage| |License|

Installation
------------
``sprockets.mixins.media_type`` is available on the
`Python Package Index <https://pypi.python.org/pypi/sprockets.mixins.media_type>`_
and can be installed via ``pip`` or ``easy_install``:

.. code:: bash

  pip install sprockets.mixins.media_type

Documentation
-------------
https://sprocketsmixinsmedia_type.readthedocs.org

Example
-------
The following example demonstrates how to use the Mix-in to handle media
type validation and serialization.

.. code:: python

    from tornado import web, gen
    from sprockets.mixins import media_type


    class MyRequestHandler(media_type.MediaTypeMixin, web.RequestHandler):

            @gen.coroutine
            def post(self, **kwargs):
                # Validate the Content-Type header using the Mix-in
                if not self.is_valid_content_type():
                    self.set_status(415, 'Unsupported content type')
                    self.finish()
                    return

                # Deserialize your request payload
                data = self.decode_request()

                # Ensure that you get some data out of it!
                if not data:
                    self.set_status(400)
                    self.finish()
                    return

                # Manipulate your data and do business stuff with it
                data.pop('the_key')

                self.set_status(200)

                # Automatically serialize your data using the HTTP Accept headers
                self.write(data)

            @gen.coroutine
            def get(self, some_id):
                # Validate the Accept headers using the Mix-in
                if not self.is_valid_accept_header():
                    self.set_status(406, 'Invalid Accept header')
                    self.finish()
                    return

                # Maybe do some lookups from the database or get some data from somewhere
                data = {'some_id': some_id}

                self.set_status(200)

                # Automatically serialize your data using the HTTP Accept headers
                self.write(data)


Version History
---------------
Available at https://sprocketsmixinsmedia_type.readthedocs.org/en/latest/history.html

.. |Version| image:: https://img.shields.io/pypi/v/sprockets.mixins.media_type.svg?
   :target: http://badge.fury.io/py/sprockets.mixins.media_type

.. |Status| image:: https://img.shields.io/travis/sprockets/sprockets.mixins.media_type.svg?
   :target: https://travis-ci.org/sprockets/sprockets.mixins.media_type

.. |Coverage| image:: https://img.shields.io/codecov/c/github/sprockets/sprockets.mixins.media_type.svg?
   :target: https://codecov.io/github/sprockets/sprockets.mixins.media_type?branch=master

.. |Downloads| image:: https://img.shields.io/pypi/dm/sprockets.mixins.media_type.svg?
   :target: https://pypi.python.org/pypi/sprockets.mixins.media_type

.. |License| image:: https://img.shields.io/pypi/l/sprockets.mixins.media_type.svg?
   :target: https://sprockets.mixins.media_type.readthedocs.org
