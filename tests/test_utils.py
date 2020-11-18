import onelogin
from django.test import RequestFactory, TestCase
from django.test.utils import override_settings

from saml2_pro_auth.utils import (
    SAMLSettingsError,
    init_saml_auth,
    prepare_django_request,
)


class TestUtils(TestCase):
    def test_init_saml_auth(self):
        factory = RequestFactory()
        request = factory.get(
            "/sso/saml/?provider=classProvider", **dict(HTTP_HOST="example.com")
        )
        auth_obj, req, user_map = init_saml_auth(request, "classProvider")
        self.assertTrue(isinstance(auth_obj, onelogin.saml2.auth.OneLogin_Saml2_Auth))
        self.assertTrue(isinstance(req, dict))

    def test_get_provider_config_with_missing_provider(self):
        factory = RequestFactory()
        request = factory.get(
            "/sso/saml/?provider=MissingProvider", **dict(HTTP_HOST="example.com")
        )
        self.assertRaises(SAMLSettingsError, init_saml_auth, request, "MissingProvider")

    def test_prepare_http_request_with_GET_no_proxy(self):
        factory = RequestFactory()
        request = factory.get(
            "/sso/saml/?provider=classProvider", **dict(HTTP_HOST="example.com")
        )
        req = prepare_django_request(request)

        self.assertEqual(req["get_data"]["provider"], "classProvider")
        self.assertEqual(req["https"], "off")
        self.assertEqual(req["script_name"], "/sso/saml/")
        self.assertEqual(req["http_host"], "example.com")

    def test_prepare_https_request_with_GET_no_proxy(self):
        factory = RequestFactory()
        request = factory.get(
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
        factory = RequestFactory()
        request = factory.get(
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
        factory = RequestFactory()
        request = factory.get(
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
        factory = RequestFactory()
        request = factory.post(
            "/sso/saml/?provider=classProvider", **dict(HTTP_HOST="example.com")
        )
        req = prepare_django_request(request)

        self.assertEqual(req["get_data"]["provider"], "classProvider")
        self.assertEqual(req["https"], "off")
        self.assertEqual(req["script_name"], "/sso/saml/")
        self.assertEqual(req["http_host"], "example.com")

    def test_prepare_https_request_with_POST_no_proxy(self):
        factory = RequestFactory()
        request = factory.post(
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
        factory = RequestFactory()
        request = factory.post(
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
        factory = RequestFactory()
        request = factory.post(
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

    @override_settings(SAML_OVERRIDE_HOSTNAME="abc.example.org")
    def test_prepare_request_with_overridden_host(self):
        factory = RequestFactory()
        request = factory.post(
            "/sso/saml/classProvider/acs/",
            **dict(
                HTTP_HOST="garbage.com",
            )
        )
        req = prepare_django_request(request)
        self.assertEqual(req["script_name"], "/sso/saml/classProvider/acs/")
        self.assertEqual(req["http_host"], "abc.example.org")
