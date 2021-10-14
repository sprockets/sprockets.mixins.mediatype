import base64
import datetime
import json
import math
import os
import pickle
import struct
import typing
import unittest.mock
import uuid

from ietfparse import algorithms
from tornado import httputil, testing, web
import umsgpack

from sprockets.mixins.mediatype import (content, handlers, transcoders,
                                        type_info)
import examples


class UTC(datetime.tzinfo):
    ZERO = datetime.timedelta(0)

    def utcoffset(self, dt):
        return self.ZERO

    def dst(self, dt):
        return self.ZERO

    def tzname(self, dt):
        return 'UTC'


class Context:
    """Super simple class to call setattr on"""
    def __init__(self):
        self.settings = {}


def pack_string(obj):
    """Optimally pack a string according to msgpack format"""
    payload = str(obj).encode('ASCII')
    pl = len(payload)
    if pl < (2**5):
        prefix = struct.pack('B', 0b10100000 | pl)
    elif pl < (2**8):
        prefix = struct.pack('BB', 0xD9, pl)
    elif pl < (2**16):
        prefix = struct.pack('>BH', 0xDA, pl)
    else:
        prefix = struct.pack('>BI', 0xDB, pl)
    return prefix + payload


def pack_bytes(payload):
    """Optimally pack a byte string according to msgpack format"""
    pl = len(payload)
    if pl < (2**8):
        prefix = struct.pack('BB', 0xC4, pl)
    elif pl < (2**16):
        prefix = struct.pack('>BH', 0xC5, pl)
    else:
        prefix = struct.pack('>BI', 0xC6, pl)
    return prefix + payload


class SendResponseTests(testing.AsyncHTTPTestCase):
    application: typing.Union[None, web.Application]

    def setUp(self):
        self.application = None
        super().setUp()

    def get_app(self):
        self.application = examples.make_application()
        return self.application

    def test_that_content_type_default_works(self):
        response = self.fetch('/',
                              method='POST',
                              body='{}',
                              headers={'Content-Type': 'application/json'})
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers['Content-Type'],
                         'application/json; charset="utf-8"')

    def test_that_missing_content_type_uses_default(self):
        response = self.fetch('/',
                              method='POST',
                              body='{}',
                              headers={
                                  'Accept': 'application/xml',
                                  'Content-Type': 'application/json'
                              })
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers['Content-Type'],
                         'application/json; charset="utf-8"')

    def test_that_accept_header_is_obeyed(self):
        response = self.fetch('/',
                              method='POST',
                              body='{}',
                              headers={
                                  'Accept': 'application/msgpack',
                                  'Content-Type': 'application/json'
                              })
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers['Content-Type'],
                         'application/msgpack')

    def test_that_default_content_type_is_set_on_response(self):
        response = self.fetch('/',
                              method='POST',
                              body=umsgpack.packb({}),
                              headers={'Content-Type': 'application/msgpack'})
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers['Content-Type'],
                         'application/json; charset="utf-8"')

    def test_that_vary_header_is_set(self):
        response = self.fetch('/',
                              method='POST',
                              body=umsgpack.packb({}),
                              headers={'Content-Type': 'application/msgpack'})
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers['Vary'], 'Accept')

    def test_that_accept_header_with_suffix_is_obeyed(self):
        content.add_transcoder(
            self._app,
            transcoders.MsgPackTranscoder(content_type='expected/content'),
            'application/vendor+msgpack')
        response = self.fetch('/',
                              method='POST',
                              body='{}',
                              headers={
                                  'Accept': 'application/vendor+msgpack',
                                  'Content-Type': 'application/json'
                              })
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers['Content-Type'], 'expected/content')

    def test_that_no_default_content_type_will_406(self):
        # NB if the Accept header is omitted, then a default of `*/*` will
        # be used which results in a match against any registered handler.
        # Using an accept header forces the "no match" case.
        settings = content.get_settings(self.application, force_instance=True)
        settings.default_content_type = None
        settings.default_encoding = None
        response = self.fetch('/',
                              method='POST',
                              body='{}',
                              headers={
                                  'Accept': 'application/xml',
                                  'Content-Type': 'application/json',
                              })
        self.assertEqual(response.code, 406)

    def test_misconfigured_default_content_type(self):
        settings = content.get_settings(self.application, force_instance=True)
        settings.default_content_type = 'application/xml'
        response = self.fetch('/',
                              method='POST',
                              body='{}',
                              headers={'Content-Type': 'application/json'})
        self.assertEqual(response.code, 500)

    def test_that_response_content_type_can_be_set(self):
        class FooGenerator(content.ContentMixin, web.RequestHandler):
            def get(self):
                self.set_header('Content-Type', 'application/foo+json')
                self.send_response({'foo': 'bar'}, set_content_type=False)

        self.application.add_handlers(r'.*', [web.url(r'/foo', FooGenerator)])
        response = self.fetch('/foo')
        self.assertEqual(200, response.code)
        self.assertEqual('application/foo+json',
                         response.headers.get('Content-Type'))


class GetRequestBodyTests(testing.AsyncHTTPTestCase):
    def setUp(self):
        self.app = None
        super().setUp()

    def get_app(self):
        self.app = examples.make_application()
        return self.app

    def test_that_request_with_unhandled_type_results_in_415(self):
        response = self.fetch('/',
                              method='POST',
                              headers={'Content-Type': 'application/xml'},
                              body=('<request><name>value</name>'
                                    '<embedded><utf8>\u2731</utf8></embedded>'
                                    '</request>').encode('utf-8'))
        self.assertEqual(response.code, 415)

    def test_that_msgpack_request_returns_default_type(self):
        body = {'name': 'value', 'embedded': {'utf8': '\u2731'}}
        response = self.fetch('/',
                              method='POST',
                              body=umsgpack.packb(body),
                              headers={'Content-Type': 'application/msgpack'})
        self.assertEqual(response.code, 200)
        self.assertEqual(json.loads(response.body.decode('utf-8')), body)

    def test_that_invalid_data_returns_400(self):
        response = self.fetch(
            '/',
            method='POST',
            headers={'Content-Type': 'application/json'},
            body=('<?xml version="1.0"?><methodCall><methodName>echo'
                  '</methodName><params><param><value><str>Hi</str></value>'
                  '</param></params></methodCall>').encode('utf-8'))
        self.assertEqual(response.code, 400)

    def test_that_content_type_suffix_is_handled(self):
        content.add_transcoder(self._app, transcoders.JSONTranscoder(),
                               'application/vendor+json')
        body = {'hello': 'world'}
        response = self.fetch(
            '/',
            method='POST',
            body=json.dumps(body),
            headers={'Content-Type': 'application/vendor+json'})
        self.assertEqual(response.code, 200)
        self.assertEqual(json.loads(response.body.decode()), body)

    def test_that_invalid_content_types_result_in_bad_request(self):
        content.set_default_content_type(self.app, None, None)
        response = self.fetch('/',
                              method='POST',
                              body='{"hi":"there"}',
                              headers={'Content-Type': 'application-json'})
        self.assertEqual(response.code, 400)


class MixinCacheTests(unittest.TestCase):
    def setUp(self):
        super().setUp()

        self.transcoder = transcoders.JSONTranscoder()

        application = unittest.mock.Mock()
        application.settings = {}
        application.ui_methods = {}
        content.install(application, 'application/json', 'utf-8')
        content.add_transcoder(application, self.transcoder)

        request = httputil.HTTPServerRequest(
            'POST',
            '/',
            body=b'{}',
            connection=unittest.mock.Mock(),
            headers=httputil.HTTPHeaders({'Content-Type': 'application/json'}),
        )

        self.handler = content.ContentMixin(application, request)

    def test_that_best_response_type_is_cached(self):
        with unittest.mock.patch(
                'sprockets.mixins.mediatype.content.algorithms.'
                'select_content_type',
                side_effect=algorithms.select_content_type
        ) as select_content_type:
            first = self.handler.get_response_content_type()
            second = self.handler.get_response_content_type()

            self.assertIs(first, second)
            self.assertEqual(1, select_content_type.call_count)

    def test_that_request_body_is_cached(self):
        self.transcoder.from_bytes = unittest.mock.Mock(
            wraps=self.transcoder.from_bytes)
        first = self.handler.get_request_body()
        second = self.handler.get_request_body()
        self.assertIs(first, second)
        self.assertEqual(1, self.transcoder.from_bytes.call_count)


class JSONTranscoderTests(unittest.TestCase):
    def setUp(self):
        super().setUp()
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

    def test_that_registered_content_types_are_normalized(self):
        settings = content.ContentSettings()
        handler = object()
        settings['application/json; VerSion=foo; type=WhatEver'] = handler
        self.assertIs(settings['application/json; type=whatever; version=foo'],
                      handler)
        self.assertIn('application/json; type=whatever; version=foo',
                      (str(c) for c in settings.available_content_types))

    def test_that_normalized_content_types_do_not_overwrite(self):
        settings = content.ContentSettings()
        settings['application/json; charset=UTF-8'] = handler = object()
        settings['application/json; charset=utf-8'] = object()
        self.assertEqual(len(settings.available_content_types), 1)
        self.assertEqual(settings.available_content_types[0].content_type,
                         'application')
        self.assertEqual(settings.available_content_types[0].content_subtype,
                         'json')
        self.assertEqual(settings['application/json; charset=utf-8'], handler)

    def test_that_setting_no_default_content_type_warns(self):
        settings = content.ContentSettings()
        with self.assertWarns(DeprecationWarning):
            settings.default_content_type = None


class ContentFunctionTests(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.context = Context()

    def test_that_add_binary_content_type_creates_binary_handler(self):
        settings = content.install(self.context, 'application/octet-stream')
        content.add_binary_content_type(self.context,
                                        'application/vnd.python.pickle',
                                        pickle.dumps, pickle.loads)
        transcoder = settings['application/vnd.python.pickle']
        self.assertIsInstance(transcoder, handlers.BinaryContentHandler)
        self.assertIs(transcoder._pack, pickle.dumps)
        self.assertIs(transcoder._unpack, pickle.loads)

    def test_that_add_text_content_type_creates_text_handler(self):
        settings = content.install(self.context, 'application/json')
        content.add_text_content_type(self.context, 'application/json', 'utf8',
                                      json.dumps, json.loads)
        transcoder = settings['application/json']
        self.assertIsInstance(transcoder, handlers.TextContentHandler)
        self.assertIs(transcoder._dumps, json.dumps)
        self.assertIs(transcoder._loads, json.loads)

    def test_that_add_text_content_type_discards_charset_parameter(self):
        settings = content.install(self.context, 'application/json', 'utf-8')
        content.add_text_content_type(self.context,
                                      'application/json;charset=UTF-8', 'utf8',
                                      json.dumps, json.loads)
        transcoder = settings['application/json']
        self.assertIsInstance(transcoder, handlers.TextContentHandler)

    def test_that_install_creates_settings(self):
        settings = content.install(self.context, 'application/json', 'utf8')
        self.assertIsNotNone(settings)
        self.assertEqual(settings.default_content_type, 'application/json')
        self.assertEqual(settings.default_encoding, 'utf8')

    def test_that_get_settings_returns_none_when_no_settings(self):
        settings = content.get_settings(self.context)
        self.assertIsNone(settings)

    def test_that_get_settings_returns_installed_settings(self):
        settings = content.install(self.context, 'application/xml', 'utf8')
        other_settings = content.get_settings(self.context)
        self.assertIs(settings, other_settings)

    def test_that_get_settings_will_create_instance_if_requested(self):
        settings = content.get_settings(self.context, force_instance=True)
        self.assertIsNotNone(settings)
        self.assertIs(content.get_settings(self.context), settings)


class MsgPackTranscoderTests(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.transcoder = transcoders.MsgPackTranscoder()

    def test_that_strings_are_dumped_as_strings(self):
        dumped = self.transcoder.packb('foo')
        self.assertEqual(self.transcoder.unpackb(dumped), 'foo')
        self.assertEqual(dumped, pack_string('foo'))

    def test_that_none_is_packed_as_nil_byte(self):
        self.assertEqual(self.transcoder.packb(None), b'\xC0')

    def test_that_bools_are_dumped_appropriately(self):
        self.assertEqual(self.transcoder.packb(False), b'\xC2')
        self.assertEqual(self.transcoder.packb(True), b'\xC3')

    def test_that_ints_are_packed_appropriately(self):
        self.assertEqual(self.transcoder.packb((2**7) - 1), b'\x7F')
        self.assertEqual(self.transcoder.packb(2**7), b'\xCC\x80')
        self.assertEqual(self.transcoder.packb(2**8), b'\xCD\x01\x00')
        self.assertEqual(self.transcoder.packb(2**16), b'\xCE\x00\x01\x00\x00')
        self.assertEqual(self.transcoder.packb(2**32),
                         b'\xCF\x00\x00\x00\x01\x00\x00\x00\x00')

    def test_that_negative_ints_are_packed_accordingly(self):
        self.assertEqual(self.transcoder.packb(-(2**0)), b'\xFF')
        self.assertEqual(self.transcoder.packb(-(2**5)), b'\xE0')
        self.assertEqual(self.transcoder.packb(-(2**7)), b'\xD0\x80')
        self.assertEqual(self.transcoder.packb(-(2**15)), b'\xD1\x80\x00')
        self.assertEqual(self.transcoder.packb(-(2**31)),
                         b'\xD2\x80\x00\x00\x00')
        self.assertEqual(self.transcoder.packb(-(2**63)),
                         b'\xD3\x80\x00\x00\x00\x00\x00\x00\x00')

    def test_that_lists_are_treated_as_arrays(self):
        dumped = self.transcoder.packb(list())
        self.assertEqual(self.transcoder.unpackb(dumped), [])
        self.assertEqual(dumped, b'\x90')

    def test_that_tuples_are_treated_as_arrays(self):
        dumped = self.transcoder.packb(tuple())
        self.assertEqual(self.transcoder.unpackb(dumped), [])
        self.assertEqual(dumped, b'\x90')

    def test_that_sets_are_treated_as_arrays(self):
        dumped = self.transcoder.packb(set())
        self.assertEqual(self.transcoder.unpackb(dumped), [])
        self.assertEqual(dumped, b'\x90')

    def test_that_unhandled_objects_raise_type_error(self):
        with self.assertRaises(TypeError):
            self.transcoder.packb(object())

    def test_that_uuids_are_dumped_as_strings(self):
        uid = uuid.uuid4()
        dumped = self.transcoder.packb(uid)
        self.assertEqual(self.transcoder.unpackb(dumped), str(uid))
        self.assertEqual(dumped, pack_string(uid))

    def test_that_datetimes_are_dumped_in_isoformat(self):
        now = datetime.datetime.now()
        dumped = self.transcoder.packb(now)
        self.assertEqual(self.transcoder.unpackb(dumped), now.isoformat())
        self.assertEqual(dumped, pack_string(now.isoformat()))

    def test_that_tzaware_datetimes_include_tzoffset(self):
        now = datetime.datetime.now().replace(tzinfo=UTC())
        self.assertTrue(now.isoformat().endswith('+00:00'))
        dumped = self.transcoder.packb(now)
        self.assertEqual(self.transcoder.unpackb(dumped), now.isoformat())
        self.assertEqual(dumped, pack_string(now.isoformat()))

    def test_that_bytes_are_sent_as_bytes(self):
        data = bytes(os.urandom(127))
        dumped = self.transcoder.packb(data)
        self.assertEqual(self.transcoder.unpackb(dumped), data)
        self.assertEqual(dumped, pack_bytes(data))

    def test_that_bytearrays_are_sent_as_bytes(self):
        data = bytearray(os.urandom(127))
        dumped = self.transcoder.packb(data)
        self.assertEqual(self.transcoder.unpackb(dumped), data)
        self.assertEqual(dumped, pack_bytes(data))

    def test_that_memoryviews_are_sent_as_bytes(self):
        data = memoryview(os.urandom(127))
        dumped = self.transcoder.packb(data)
        self.assertEqual(self.transcoder.unpackb(dumped), data)
        self.assertEqual(dumped, pack_bytes(data.tobytes()))

    def test_that_utf8_values_can_be_forced_to_bytes(self):
        data = b'a ascii value'
        dumped = self.transcoder.packb(data)
        self.assertEqual(self.transcoder.unpackb(dumped), data)
        self.assertEqual(dumped, pack_bytes(data))

    def test_that_dicts_are_sent_as_maps(self):
        data = {'compact': True, 'schema': 0}
        dumped = self.transcoder.packb(data)
        self.assertEqual(b'\x82\xA7compact\xC3\xA6schema\x00', dumped)

    def test_that_transcoder_creation_fails_if_umsgpack_is_missing(self):
        with unittest.mock.patch(
                'sprockets.mixins.mediatype.transcoders.umsgpack',
                new_callable=lambda: None):
            with self.assertRaises(RuntimeError):
                transcoders.MsgPackTranscoder()


class FormUrlEncodingTranscoderTests(unittest.TestCase):
    transcoder: type_info.Transcoder

    def setUp(self):
        super().setUp()
        self.transcoder = transcoders.FormUrlEncodedTranscoder()

    def test_simple_deserialization(self):
        body = self.transcoder.from_bytes(
            b'number=12&boolean=true&null=null&string=anything%20really&empty='
        )
        self.assertEqual(body['number'], '12')
        self.assertEqual(body['boolean'], 'true')
        self.assertEqual(body['empty'], '')
        self.assertEqual(body['null'], 'null')
        self.assertEqual(body['string'], 'anything really')

    def test_deserialization_edge_cases(self):
        body = self.transcoder.from_bytes(b'')
        self.assertEqual({}, body)

        body = self.transcoder.from_bytes(b'&')
        self.assertEqual({}, body)

        body = self.transcoder.from_bytes(b'empty&&=no-name&no-value=')
        self.assertEqual({'empty': '', '': 'no-name', 'no-value': ''}, body)

        body = self.transcoder.from_bytes(b'repeated=1&repeated=2')
        self.assertEqual({'repeated': '2'}, body)

    def test_that_deserialization_encoding_can_be_overridden(self):
        body = self.transcoder.from_bytes(b'kolor=%bf%F3%b3ty',
                                          encoding='iso-8859-2')
        self.assertEqual({'kolor': 'żółty'}, body)

    def test_simple_serialization(self):
        now = datetime.datetime.now()
        id_val = uuid.uuid4()
        content_type, result = self.transcoder.to_bytes({
            'integer': 12,
            'float': math.pi,
            'string': 'percent quoted',
            'datetime': now,
            'id': id_val,
        })
        self.assertEqual(content_type, 'application/x-www-formurlencoded')
        self.assertEqual(
            result.decode(), '&'.join([
                'integer=12',
                f'float={math.pi}',
                'string=percent%20quoted',
                'datetime=' + now.isoformat().replace(':', '%3A'),
                f'id={id_val}',
            ]))

    def test_that_serialization_encoding_can_be_overridden(self):
        _, result = self.transcoder.to_bytes([('kolor', 'żółty')],
                                             encoding='iso-8859-2')
        self.assertEqual(b'kolor=%bf%f3%b3ty', result.lower())

    def test_serialization_edge_cases(self):
        _, result = self.transcoder.to_bytes([
            ('', ''),
            ('', True),
            ('', False),
            ('', None),
            ('name', None),
        ])
        self.assertEqual(b'=&=true&=false&&name', result)

    def test_serialization_using_plusses(self):
        self.transcoder: transcoders.FormUrlEncodedTranscoder

        self.transcoder.options.space_as_plus = True
        _, result = self.transcoder.to_bytes({'value': 'with space'})
        self.assertEqual(b'value=with+space', result)

        self.transcoder.options.space_as_plus = False
        _, result = self.transcoder.to_bytes({'value': 'with space'})
        self.assertEqual(b'value=with%20space', result)

    def test_that_serializing_unsupported_types_fails(self):
        with self.assertRaises(TypeError):
            self.transcoder.to_bytes({'unsupported': object()})

    def test_that_required_octets_are_encoded(self):
        # build the set of all characters required to be encoded by
        # https://url.spec.whatwg.org/#percent-encoded-bytes
        pct_chrs = typing.cast(typing.Set[str], set())
        pct_chrs.update({c for c in ' "#<>'})  # query set
        pct_chrs.update({c for c in '?`{}'})  # path set
        pct_chrs.update({c for c in '/:;=@[^|'})  # userinfo set
        pct_chrs.update({c for c in '$%&+,'})  # component set
        pct_chrs.update({c for c in "!'()~"})  # formurlencoding set

        test_string = ''.join(pct_chrs)
        expected = ''.join('%{:02X}'.format(ord(c)) for c in test_string)
        expected = f'test_string={expected}'.encode()
        _, result = self.transcoder.to_bytes({'test_string': test_string})
        self.assertEqual(expected, result)

    def test_serialization_of_primitives(self):
        id_val = uuid.uuid4()
        expectations = {
            None: b'',
            'a string': b'a%20string',
            10: b'10',
            2.3: str(2.3).encode(),
            True: b'true',
            False: b'false',
            b'\xfe\xed\xfa\xce': b'%FE%ED%FA%CE',
            memoryview(b'\xfe\xed\xfa\xce'): b'%FE%ED%FA%CE',
            id_val: str(id_val).encode(),
        }
        for value, expected in expectations.items():
            _, result = self.transcoder.to_bytes(value)
            self.assertEqual(expected, result)

    def test_serialization_with_empty_literal_map(self):
        self.transcoder: transcoders.FormUrlEncodedTranscoder
        self.transcoder.options.literal_mapping.clear()
        for value in {None, True, False}:
            with self.assertRaises(TypeError):
                self.transcoder.to_bytes(value)

    def test_serialization_of_sequences(self):
        sequence = [[1, 2, 3], {1, 2, 3}, (1, 2, 3)]
        for value in sequence:
            with self.assertRaises(TypeError):
                self.transcoder.to_bytes(value)
