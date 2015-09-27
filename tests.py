import base64
import datetime
import json
import unittest
import uuid

from tornado import testing
import umsgpack

from sprockets.mixins.mediatype import transcoders
import examples


class UTC(datetime.tzinfo):
    ZERO = datetime.timedelta(0)

    def utcoffset(self, _):
        return self.ZERO

    def tzname(self, _):
        return 'UTC'

    def dst(self, _):
        return self.ZERO


class SendResponseTests(testing.AsyncHTTPTestCase):

    def get_app(self):
        return examples.make_application(debug=True)

    def test_that_content_type_default_works(self):
        response = self.fetch('/', method='POST', body='{}',
                              headers={'Content-Type': 'application/json'})
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers['Content-Type'],
                         'application/json; charset="utf-8"')

    def test_that_missing_content_type_uses_default(self):
        response = self.fetch('/', method='POST', body='{}',
                              headers={'Accept': 'application/xml',
                                       'Content-Type': 'application/json'})
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers['Content-Type'],
                         'application/json; charset="utf-8"')

    def test_that_accept_header_is_obeyed(self):
        response = self.fetch('/', method='POST', body='{}',
                              headers={'Accept': 'application/msgpack',
                                       'Content-Type': 'application/json'})
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers['Content-Type'],
                         'application/msgpack')

    def test_that_default_content_type_is_set_on_response(self):
        response = self.fetch('/', method='POST', body=umsgpack.packb('{}'),
                              headers={'Content-Type': 'application/msgpack'})
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers['Content-Type'],
                         'application/json; charset="utf-8"')


class GetRequestBodyTests(testing.AsyncHTTPTestCase):

    def get_app(self):
        return examples.make_application(debug=True)

    def test_that_request_with_unhandled_type_results_in_415(self):
        response = self.fetch(
            '/', method='POST', headers={'Content-Type': 'application/xml'},
            body=(u'<request><name>value</name>'
                  u'<embedded><utf8>\u2731</utf8></embedded>'
                  u'</request>').encode('utf-8'))
        self.assertEqual(response.code, 415)

    def test_that_msgpack_request_returns_default_type(self):
        body = {
            'name': 'value',
            'embedded': {
                'utf8': u'\u2731'
            }
        }
        response = self.fetch('/', method='POST', body=umsgpack.packb(body),
                              headers={'Content-Type': 'application/msgpack'})
        self.assertEqual(response.code, 200)
        self.assertEqual(json.loads(response.body.decode('utf-8')), body)


class JSONTranscoderTests(unittest.TestCase):

    def setUp(self):
        super(JSONTranscoderTests, self).setUp()
        self.transcoder = transcoders.JSONTranscoder()

    def test_that_encoding_unrecognized_type_raise_type_error(self):
        with self.assertRaises(TypeError):
            self.transcoder.to_bytes(object())

    def test_that_datetimes_encoded_as_iso8601(self):
        value = datetime.datetime.utcnow().replace(tzinfo=UTC())
        _, json_bytes = self.transcoder.to_bytes(value)
        self.assertEqual(
            json_bytes,
            value.strftime('"%Y-%m-%dT%H:%M:%S.%f%z"').encode('ASCII'))

    def test_that_uuids_are_encoded_as_strings(self):
        value = uuid.uuid4()
        _, json_bytes = self.transcoder.to_bytes(value)
        self.assertEqual(json_bytes, '"{}"'.format(value).encode('ASCII'))

    def test_that_bytes_are_base64_encoded(self):
        value = bytearray(range(0, 255))
        _, json_bytes = self.transcoder.to_bytes(value)
        self.assertEqual(
            json_bytes.decode('ASCII'),
            '"{}"'.format(base64.b64encode(value).decode('ASCII')))
