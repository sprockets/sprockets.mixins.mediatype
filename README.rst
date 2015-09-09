sprockets.mixins.media_type
===========================
A mixin that performs Content-Type negotiation and request/response
(de)serialization.

|Documentation| |Build Badge| |Package Info|

This mix-in adds two methods to a ``tornado.web.RequestHandler`` instance:

- ``get_request_body() -> dict``: deserializes the request body according
  to the HTTP ``Content-Type`` header and returns the deserialized body.
- ``send_response(object)``: serializes the response into the content type
  requested by the ``Accept`` header.

Support for a content types is enabled by calling either the
``add_binary_content_type`` or ``add_text_content_type`` function with the
``tornado.web.Application`` instance, the content type, encoding and decoding
functions as parameters:

.. code-block:: python

   import json

   from sprockets.mixins import media_type
   from tornado import web

   def make_application():
       application = web.Application([
           # insert your handlers here
       ])

       media_type.add_text_content_type(application,
                                        'application/json', 'utf-8',
                                        json.dumps, json.loads)

       return application

The *add content type* functions will add a attribute to the ``Application``
instance that the mix-in uses to manipulate the request and response bodies.

.. code-block:: python

   from sprockets.mixins import media_type
   from tornado import web

   class SomeHandler(media_type.ContentMixin, web.RequestHandler):
       def get(self):
           self.send_response({'data': 'value'})
           self.finish()

       def post(self):
           body = self.get_request_body()
           # do whatever
           self.send_response({'action': 'performed'})
           self.finish()

Based on the settings stored in the ``Application`` instance and the HTTP
headers, the request and response data will be handled correctly or the
appropriate HTTP exceptions will be raised.

.. |Documentation| image:: https://readthedocs.org/projects/sprocketsmixinsmedia-type/badge/?version=latest
   :target: https://sprocketsmixinsmedia-type.readthedocs.org/
.. |Build Badge| image:: https://travis-ci.org/sprockets/sprockets.mixins.media_type.svg
   :target: https://travis-ci.org/sprockets/sprockets.mixins.media_type
.. |Package Info| image:: https://img.shields.io/pypi/v/sprockets.mixins.mediatype.svg
   :target: https://pypi.python.org/sprockets.mixins.mediatype
