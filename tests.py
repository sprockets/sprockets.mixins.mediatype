"""
Tests for the sprockets.mixins.media_type package

"""
import json
import unittest
import uuid

from sprockets.mixins import media_type
from tornado import web, gen, testing
import msgpack


class MyRequestHandler(media_type.MediaTypeMixin, web.RequestHandler):

    @gen.coroutine
    def post(self, **kwargs):
        if not self.is_valid_content_type():
            self.set_status(415, 'Unsupported content type')
            self.finish()
            return

        data = self.decode_request()

        if not data:
            self.set_status(400)
            self.finish()
            return

        data.pop('the_key')
        self.set_status(200)
        self.write(data)

    @gen.coroutine
    def get(self, some_id):
        if not self.is_valid_accept_header():
            self.set_status(419, 'Invalid Accept header')
            self.finish()
            return

        data = {'some_id': some_id}
        self.set_status(200)
        self.write(data)


class TestSetApplication(testing.AsyncHTTPTestCase):

    def get_app(self):
        return web.Application(
            [web.url(r'/(?P<some_id>.*)', MyRequestHandler)]
        )

    def test_accept_header_validation(self):
        headers = {'Accept': 'application/pizza'}
        response = self.fetch('/', method='GET', headers=headers)
        self.assertEqual(419, response.code)

    def test_content_type_header_validation(self):
        headers = {'Content-Type': 'application/pizza'}
        response = self.fetch('/', method='POST', headers=headers, body='{}')
        self.assertEqual(415, response.code)

    def test_json_payload_is_deserialized_properly(self):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        payload = json.dumps({'the_key': 1, 'other_key': 2})
        response = self.fetch('/', method='POST', headers=headers,
                              body=payload)

        self.assertEqual(200, response.code)
        self.assertEqual({'other_key': 2},
                         json.loads(response.body.decode('utf8')))

    def test_msgpack_payload_is_deserialized_properly(self):
        headers = {
            'Content-Type': 'application/msgpack',
            'Accept': 'application/msgpack',
        }
        payload = msgpack.dumps({'the_key': 1, 'other_key': 2})
        response = self.fetch('/', method='POST', headers=headers,
                              body=payload)

        self.assertEqual(200, response.code)
        self.assertEqual({'other_key': 2},
                         msgpack.loads(response.body, encoding='utf8'))

    def test_missing_payload(self):
        headers = {
            'Content-Type': 'application/msgpack',
            'Accept': 'application/msgpack',
        }
        response = self.fetch('/', method='POST', headers=headers, body='')

        self.assertEqual(400, response.code)
