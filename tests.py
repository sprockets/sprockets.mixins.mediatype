from tornado import testing

import examples


class ContentTypeTests(testing.AsyncHTTPTestCase):

    def get_app(self):
        return examples.make_application(debug=True)

    def test_that_content_type_default_works(self):
        response = self.fetch('/', method='POST',
                              body='{"attribute": "value"}',
                              headers={'Content-Type': 'application/json'})
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers['Content-Type'],
                         'application/json; charset="utf-8"')

    def test_that_missing_content_type_uses_default(self):
        response = self.fetch('/', method='POST', body='{}',
                              headers={'Accept': 'application/xml'})
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers['Content-Type'],
                         'application/json; charset="utf-8"')
