sprockets.mixins.mediatype
==========================
A mixin that performs Content-Type negotiation and request/response
(de)serialization.

|Documentation| |Build Badge| |Package Info|

This mix-in adds two methods to a ``tornado.web.RequestHandler`` instance:

- ``get_request_body() -> dict``: deserializes the request body according
  to the HTTP ``Content-Type`` header and returns the deserialized body.
- ``send_response(object)``: serializes the response into the content type
  requested by the ``Accept`` header.

Before adding support for specific content types, you SHOULD install the
content settings into your ``tornado.web.Application`` instance.  If you
don't install the content settings, then an instance will be created for
you by the mix-in; however, the created instance will be empty.  You
should already have a function that creates the ``Application`` instance.
If you don't, now is a good time to add one.

.. code-block:: python

   from sprockets.mixins.mediatype import content
   from tornado import web

   def make_application():
       application = web.Application([
           # insert your handlers here
       ])
       content.install(application, 'application/json', 'utf-8')
       return application

Support for a content types is enabled by calling ``add_binary_content_type``,
``add_text_content_type`` or the ``add_transcoder`` functions with the
``tornado.web.Application`` instance, the content type, encoding and decoding
functions as parameters:

.. code-block:: python

   import json

   from sprockets.mixins.mediatype import content
   from tornado import web

   def make_application():
       application = web.Application([
           # insert your handlers here
       ])

       content.install(application, 'application/json', 'utf-8')
       content.add_text_content_type(application,
                                     'application/json', 'utf-8',
                                     json.dumps, json.loads)

       return application

The *add content type* functions will add a attribute to the ``Application``
instance that the mix-in uses to manipulate the request and response bodies.
The *add_transcoder* function is similar except that it takes an object
that implements transcoding methods instead of simple functions.  The
``transcoders`` module includes ready-to-use transcoders for a few content
types:

.. code-block:: python

   from sprockets.mixins.mediatype import content, transcoders
   from tornado import web

   def make_application():
       application = web.Application([
           # insert your handlers here
       ])

       content.install(application, 'application/json', 'utf-8')
       content.add_transcoder(application, transcoders.JSONTranscoder())

       return application

In either case, the ``ContentMixin`` uses the registered content type
information to provide transparent content type negotiation for your
request handlers.

.. code-block:: python

   from sprockets.mixins.mediatype import content
   from tornado import web

   class SomeHandler(content.ContentMixin, web.RequestHandler):
       def get(self):
           self.send_response({'data': 'value'})

       def post(self):
           body = self.get_request_body()
           # do whatever
           self.send_response({'action': 'performed'})

Based on the settings stored in the ``Application`` instance and the HTTP
headers, the request and response data will be handled correctly or the
appropriate HTTP exceptions will be raised.

.. |Documentation| image:: https://readthedocs.org/projects/sprocketsmixinsmedia-type/badge/?version=latest
   :target: https://sprocketsmixinsmedia-type.readthedocs.org/
.. |Build Badge| image:: https://travis-ci.org/sprockets/sprockets.mixins.mediatype.svg
   :target: https://travis-ci.org/sprockets/sprockets.mixins.mediatype
.. |Package Info| image:: https://img.shields.io/pypi/v/sprockets.mixins.mediatype.svg
   :target: https://pypi.python.org/pypi/sprockets.mixins.mediatype
