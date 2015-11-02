from __future__ import print_function

import json
import unittest

from tornado import testing
import msgpack

from sprockets.mixins import mediatype
import examples


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


class RegressionTests(unittest.TestCase):

    def test_that_deeply_nested_json_is_supported(self):
        # this generates as deeply nested of a JSON document as the
        # underlying json.dumps can handle
        depth = 0
        nested = {'nested': 'dict'}
        while True:
            try:
                parent = {'nested': nested}

                def f():
                    def g():
                        json.dumps(parent)
                    g()
                f()
                nested = parent
                depth += 1
            except RuntimeError:
                break
        print('this implementation can handle', depth, 'nesting levels')

        handler = mediatype._TextContentHandler('application/json',
                                                json.dumps, json.loads,
                                                'utf-8')
        _, encoded = handler.to_bytes(nested)
        self.assertEqual(handler.from_bytes(encoded), nested)
