from django.test.utils import override_settings
from django.test import TestCase
from django.conf import settings
from django.test import RequestFactory

from django_saml2_pro_auth.utils import get_provider_config, init_saml_auth, prepare_django_request

import onelogin
from .data.configs import MOCK_SAML2_CONFIG
from django_saml2_pro_auth.utils import SAMLError, SAMLSettingsError

try:
    settings.configure()
except:
    pass

CACHES = {
    'default': {
        'django.core.cache.backends.locmem.LocMemCache'
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'testingdb'
    }
}
settings.CACHES = CACHES
settings.DATABASES = DATABASES



class TestUtils(TestCase):

    @override_settings(SAML_PROVIDERS=MOCK_SAML2_CONFIG)
    def test_init_saml_auth(self):
        r = RequestFactory()
        request = r.get('/sso/saml/?provider=MyProvider', **dict(HTTP_HOST='example.com'))
        req = prepare_django_request(request)
        auth_obj = init_saml_auth(req)
        self.assertTrue(type(auth_obj) is onelogin.saml2.auth.OneLogin_Saml2_Auth)

    def test_get_provider_config_with_missing_query_str(self):
        r = RequestFactory()
        request = r.get('/sso/saml/', **dict(HTTP_HOST='example.com'))
        req = prepare_django_request(request)
        self.assertRaises(SAMLError, get_provider_config, req)

    @override_settings(SAML_PROVIDERS=MOCK_SAML2_CONFIG)
    def test_get_provider_config_with_missing_provider(self):
        r = RequestFactory()
        request = r.get('/sso/saml/?provider=MissingProvider', **dict(HTTP_HOST='example.com'))
        req = prepare_django_request(request)
        self.assertRaises(SAMLSettingsError, get_provider_config, req)

    @override_settings(SAML_PROVIDERS=MOCK_SAML2_CONFIG)
    def test_get_provider_config(self):
        r = RequestFactory()
        request = r.get('/sso/saml/?provider=MyProvider', **dict(HTTP_HOST='example.com'))
        req = prepare_django_request(request)
        config = get_provider_config(req)
        mock_cfg = MOCK_SAML2_CONFIG[0]['MyProvider']
        for top_attr in mock_cfg.keys():
            if type(top_attr) is dict:
                for key, value in top_attr.iteritems():
                    self.assertEqual(mock_cfg[key], config[key])
            else:
                self.assertEqual(mock_cfg[top_attr], config[top_attr])

    def test_prepare_http_request_with_GET_no_proxy(self):
        r = RequestFactory()
        request = r.get('/sso/saml/?provider=MyProvider', **dict(HTTP_HOST='example.com'))
        req = prepare_django_request(request)

        self.assertEqual(req['get_data']['provider'], 'MyProvider')
        self.assertEqual(req['https'], 'off')
        self.assertEqual(req['script_name'], '/sso/saml/')
        self.assertEqual(req['http_host'], 'example.com')

    def test_prepare_https_request_with_GET_no_proxy(self):
        r = RequestFactory()
        request = r.get('/sso/saml/?provider=MyProvider', secure=True, **dict(HTTP_HOST='example.com'))
        req = prepare_django_request(request)
        self.assertEqual(req['get_data']['provider'], 'MyProvider')
        self.assertEqual(req['https'], 'on')
        self.assertEqual(req['script_name'], '/sso/saml/')
        self.assertEqual(req['http_host'], 'example.com')

    def test_prepare_http_request_with_GET_plus_proxy(self):
        r = RequestFactory()
        request = r.get('/sso/saml/?provider=MyProvider', **dict(HTTP_X_FORWARDED_FOR='10.10.10.10', HTTP_X_FORWARDED_PROTO='http', HTTP_HOST='example.com'))
        req = prepare_django_request(request)
        self.assertEqual(req['get_data']['provider'], 'MyProvider')
        self.assertEqual(req['https'], 'off')
        self.assertEqual(req['script_name'], '/sso/saml/')
        self.assertEqual(req['http_host'], 'example.com')

    def test_prepare_https_request_with_GET_plus_proxy(self):
        r = RequestFactory()
        request = r.get('/sso/saml/?provider=MyProvider', **dict(HTTP_X_FORWARDED_FOR='10.10.10.10', HTTP_X_FORWARDED_PROTO='https', HTTP_HOST='example.com'))
        req = prepare_django_request(request)
        self.assertEqual(req['get_data']['provider'], 'MyProvider')
        self.assertEqual(req['https'], 'on')
        self.assertEqual(req['script_name'], '/sso/saml/')
        self.assertEqual(req['http_host'], 'example.com')

    def test_prepare_http_request_with_POST_no_proxy(self):
        r = RequestFactory()
        request = r.post('/sso/saml/?provider=MyProvider', **dict(HTTP_HOST='example.com'))
        req = prepare_django_request(request)

        self.assertEqual(req['get_data']['provider'], 'MyProvider')
        self.assertEqual(req['https'], 'off')
        self.assertEqual(req['script_name'], '/sso/saml/')
        self.assertEqual(req['http_host'], 'example.com')

    def test_prepare_https_request_with_POST_no_proxy(self):
        r = RequestFactory()
        request = r.post('/sso/saml/?provider=MyProvider', secure=True, **dict(HTTP_HOST='example.com'))
        req = prepare_django_request(request)
        self.assertEqual(req['get_data']['provider'], 'MyProvider')
        self.assertEqual(req['https'], 'on')
        self.assertEqual(req['script_name'], '/sso/saml/')
        self.assertEqual(req['http_host'], 'example.com')

    def test_prepare_http_request_with_POST_plus_proxy(self):
        r = RequestFactory()
        request = r.post('/sso/saml/?provider=MyProvider', **dict(HTTP_X_FORWARDED_FOR='10.10.10.10', HTTP_X_FORWARDED_PROTO='http', HTTP_HOST='example.com'))
        req = prepare_django_request(request)
        self.assertEqual(req['get_data']['provider'], 'MyProvider')
        self.assertEqual(req['https'], 'off')
        self.assertEqual(req['script_name'], '/sso/saml/')
        self.assertEqual(req['http_host'], 'example.com')

    def test_prepare_https_request_with_POST_plus_proxy(self):
        r = RequestFactory()
        request = r.post('/sso/saml/?provider=MyProvider', **dict(HTTP_X_FORWARDED_FOR='10.10.10.10', HTTP_X_FORWARDED_PROTO='https', HTTP_HOST='example.com'))
        req = prepare_django_request(request)
        self.assertEqual(req['get_data']['provider'], 'MyProvider')
        self.assertEqual(req['https'], 'on')
        self.assertEqual(req['script_name'], '/sso/saml/')
        self.assertEqual(req['http_host'], 'example.com')
