import base64
import datetime
import json
import os
import pickle
import sys
import unittest
import uuid

from tornado import testing
import msgpack

from sprockets.mixins.mediatype import content, handlers, transcoders
import examples


class UTC(datetime.tzinfo):
    ZERO = datetime.timedelta(0)

    def utcoffset(self, dt):
        return self.ZERO

    def dst(self, dt):
        return self.ZERO

    def tzname(self, dt):
        return 'UTC'


class Context(object):
    pass


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
        response = self.fetch('/', method='POST', body=msgpack.packb({}),
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
        response = self.fetch('/', method='POST', body=msgpack.packb(body),
                              headers={'Content-Type': 'application/msgpack'})
        self.assertEqual(response.code, 200)
        self.assertEqual(json.loads(response.body.decode('utf-8')), body)


class JSONTranscoderTests(unittest.TestCase):

    def setUp(self):
        super(JSONTranscoderTests, self).setUp()
        self.transcoder = transcoders.JSONTranscoder()

    def test_that_uuids_are_dumped_as_strings(self):
        obj = {'id': uuid.uuid4()}
        dumped = self.transcoder.dumps(obj)
        self.assertEqual(dumped.replace(' ', ''), '{"id":"%s"}' % obj['id'])

    def test_that_datetimes_are_dumped_in_isoformat(self):
        obj = {'now': datetime.datetime.now()}
        dumped = self.transcoder.dumps(obj)
        self.assertEqual(dumped.replace(' ', ''),
                         '{"now":"%s"}' % obj['now'].isoformat())

    def test_that_tzaware_datetimes_include_tzoffset(self):
        obj = {'now': datetime.datetime.now().replace(tzinfo=UTC())}
        self.assertTrue(obj['now'].isoformat().endswith('+00:00'))
        dumped = self.transcoder.dumps(obj)
        self.assertEqual(dumped.replace(' ', ''),
                         '{"now":"%s"}' % obj['now'].isoformat())

    @unittest.skipIf(sys.version_info[0] == 2, 'bytes unsupported on python 2')
    def test_that_bytes_are_base64_encoded(self):
        bin = bytes(os.urandom(127))
        dumped = self.transcoder.dumps({'bin': bin})
        self.assertEqual(
            dumped, '{"bin":"%s"}' % base64.b64encode(bin).decode('ASCII'))

    def test_that_bytearrays_are_base64_encoded(self):
        bin = bytearray(os.urandom(127))
        dumped = self.transcoder.dumps({'bin': bin})
        self.assertEqual(
            dumped, '{"bin":"%s"}' % base64.b64encode(bin).decode('ASCII'))

    def test_that_memoryviews_are_base64_encoded(self):
        bin = memoryview(os.urandom(127))
        dumped = self.transcoder.dumps({'bin': bin})
        self.assertEqual(
            dumped, '{"bin":"%s"}' % base64.b64encode(bin).decode('ASCII'))

    def test_that_unhandled_objects_raise_type_error(self):
        with self.assertRaises(TypeError):
            self.transcoder.dumps(object())


class ContentSettingsTests(unittest.TestCase):

    def test_that_from_application_creates_instance(self):
        class Context(object):
            pass

        context = Context()
        settings = content.ContentSettings.from_application(context)
        self.assertIs(content.ContentSettings.from_application(context),
                      settings)

    def test_that_handler_listed_in_available_content_types(self):
        settings = content.ContentSettings()
        settings['application/json'] = object()
        self.assertEqual(len(settings.available_content_types), 1)
        self.assertEqual(settings.available_content_types[0].content_type,
                         'application')
        self.assertEqual(settings.available_content_types[0].content_subtype,
                         'json')

    def test_that_handler_is_not_overwritten(self):
        settings = content.ContentSettings()
        settings['application/json'] = handler = object()
        settings['application/json'] = object()
        self.assertIs(settings.get('application/json'), handler)


class ContentFunctionTests(unittest.TestCase):

    def setUp(self):
        super(ContentFunctionTests, self).setUp()
        self.context = Context()

    def test_that_add_binary_content_type_creates_binary_handler(self):
        content.add_binary_content_type(self.context,
                                        'application/vnd.python.pickle',
                                        pickle.dumps, pickle.loads)
        settings = content.ContentSettings.from_application(self.context)
        transcoder = settings['application/vnd.python.pickle']
        self.assertIsInstance(transcoder, handlers.BinaryContentHandler)
        self.assertIs(transcoder._pack, pickle.dumps)
        self.assertIs(transcoder._unpack, pickle.loads)

    def test_that_add_text_content_type_creates_text_handler(self):
        content.add_text_content_type(self.context, 'application/json', 'utf8',
                                      json.dumps, json.loads)
        settings = content.ContentSettings.from_application(self.context)
        transcoder = settings['application/json']
        self.assertIsInstance(transcoder, handlers.TextContentHandler)
        self.assertIs(transcoder._dumps, json.dumps)
        self.assertIs(transcoder._loads, json.loads)
