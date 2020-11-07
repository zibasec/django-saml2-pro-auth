import onelogin
from django.test import RequestFactory, TestCase

from saml2_pro_auth.utils import (
    SAMLSettingsError,
    init_saml_auth,
    prepare_django_request,
)


class TestUtils(TestCase):
    def test_init_saml_auth(self):
        r = RequestFactory()
        request = r.get(
            "/sso/saml/?provider=classProvider", **dict(HTTP_HOST="example.com")
        )
        req = prepare_django_request(request)
        auth_obj = init_saml_auth(req)
        self.assertTrue(type(auth_obj) is onelogin.saml2.auth.OneLogin_Saml2_Auth)

    def test_get_provider_config_with_missing_provider(self):
        r = RequestFactory()
        request = r.get(
            "/sso/saml/?provider=MissingProvider", **dict(HTTP_HOST="example.com")
        )
        req = prepare_django_request(request)
        self.assertRaises(SAMLSettingsError, init_saml_auth, req)

    def test_prepare_http_request_with_GET_no_proxy(self):
        r = RequestFactory()
        request = r.get(
            "/sso/saml/?provider=classProvider", **dict(HTTP_HOST="example.com")
        )
        req = prepare_django_request(request)

        self.assertEqual(req["get_data"]["provider"], "classProvider")
        self.assertEqual(req["https"], "off")
        self.assertEqual(req["script_name"], "/sso/saml/")
        self.assertEqual(req["http_host"], "example.com")

    def test_prepare_https_request_with_GET_no_proxy(self):
        r = RequestFactory()
        request = r.get(
            "/sso/saml/?provider=classProvider",
            secure=True,
            **dict(HTTP_HOST="example.com")
        )
        req = prepare_django_request(request)
        self.assertEqual(req["get_data"]["provider"], "classProvider")
        self.assertEqual(req["https"], "on")
        self.assertEqual(req["script_name"], "/sso/saml/")
        self.assertEqual(req["http_host"], "example.com")

    def test_prepare_http_request_with_GET_plus_proxy(self):
        r = RequestFactory()
        request = r.get(
            "/sso/saml/?provider=classProvider",
            **dict(
                HTTP_X_FORWARDED_FOR="10.10.10.10",
                HTTP_X_FORWARDED_PROTO="http",
                HTTP_HOST="example.com",
            )
        )
        req = prepare_django_request(request)
        self.assertEqual(req["get_data"]["provider"], "classProvider")
        self.assertEqual(req["https"], "off")
        self.assertEqual(req["script_name"], "/sso/saml/")
        self.assertEqual(req["http_host"], "example.com")

    def test_prepare_https_request_with_GET_plus_proxy(self):
        r = RequestFactory()
        request = r.get(
            "/sso/saml/?provider=classProvider",
            **dict(
                HTTP_X_FORWARDED_FOR="10.10.10.10",
                HTTP_X_FORWARDED_PROTO="https",
                HTTP_HOST="example.com",
            )
        )
        req = prepare_django_request(request)
        self.assertEqual(req["get_data"]["provider"], "classProvider")
        self.assertEqual(req["https"], "on")
        self.assertEqual(req["script_name"], "/sso/saml/")
        self.assertEqual(req["http_host"], "example.com")

    def test_prepare_http_request_with_POST_no_proxy(self):
        r = RequestFactory()
        request = r.post(
            "/sso/saml/?provider=classProvider", **dict(HTTP_HOST="example.com")
        )
        req = prepare_django_request(request)

        self.assertEqual(req["get_data"]["provider"], "classProvider")
        self.assertEqual(req["https"], "off")
        self.assertEqual(req["script_name"], "/sso/saml/")
        self.assertEqual(req["http_host"], "example.com")

    def test_prepare_https_request_with_POST_no_proxy(self):
        r = RequestFactory()
        request = r.post(
            "/sso/saml/?provider=classProvider",
            secure=True,
            **dict(HTTP_HOST="example.com")
        )
        req = prepare_django_request(request)
        self.assertEqual(req["get_data"]["provider"], "classProvider")
        self.assertEqual(req["https"], "on")
        self.assertEqual(req["script_name"], "/sso/saml/")
        self.assertEqual(req["http_host"], "example.com")

    def test_prepare_http_request_with_POST_plus_proxy(self):
        r = RequestFactory()
        request = r.post(
            "/sso/saml/?provider=classProvider",
            **dict(
                HTTP_X_FORWARDED_FOR="10.10.10.10",
                HTTP_X_FORWARDED_PROTO="http",
                HTTP_HOST="example.com",
            )
        )
        req = prepare_django_request(request)
        self.assertEqual(req["get_data"]["provider"], "classProvider")
        self.assertEqual(req["https"], "off")
        self.assertEqual(req["script_name"], "/sso/saml/")
        self.assertEqual(req["http_host"], "example.com")

    def test_prepare_https_request_with_POST_plus_proxy(self):
        r = RequestFactory()
        request = r.post(
            "/sso/saml/?provider=classProvider",
            **dict(
                HTTP_X_FORWARDED_FOR="10.10.10.10",
                HTTP_X_FORWARDED_PROTO="https",
                HTTP_HOST="example.com",
            )
        )
        req = prepare_django_request(request)
        self.assertEqual(req["get_data"]["provider"], "classProvider")
        self.assertEqual(req["https"], "on")
        self.assertEqual(req["script_name"], "/sso/saml/")
        self.assertEqual(req["http_host"], "example.com")
