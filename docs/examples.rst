Examples
========

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
