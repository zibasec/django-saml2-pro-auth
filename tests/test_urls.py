from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import resolve, reverse

from django_saml2_pro_auth.urls import AUTH, METADATA, SAML_ROUTE


class TestURLS(TestCase):
    def test_url_constants(self):
        self.assertEqual(SAML_ROUTE, "sso/saml")
        self.assertEqual(AUTH, "^sso/saml/$")
        self.assertEqual(METADATA, "^sso/saml/metadata/$")

    def test_url_names_with_start_forward_slash(self):
        self.assertEqual(reverse("saml2_auth"), "/sso/saml/")
        self.assertEqual(reverse("metadata"), "/sso/saml/metadata/")

    def test_url_resolving_with_start_forward_slash(self):
        self.assertEqual(resolve("/sso/saml/").view_name, "saml2_auth")
        self.assertEqual(resolve("/sso/saml/metadata/").view_name, "metadata")

    @override_settings(SAML_ROUTE="/sso/saml/")
    def test_url_names_with_end_forward_slash(self):
        self.assertEqual(reverse("saml2_auth"), "/sso/saml/")
        self.assertEqual(reverse("metadata"), "/sso/saml/metadata/")

    @override_settings(SAML_ROUTE="/sso/saml/")
    def test_url_resolving_with_end_forward_slash(self):
        self.assertEqual(resolve("/sso/saml/").view_name, "saml2_auth")
        self.assertEqual(resolve("/sso/saml/metadata/").view_name, "metadata")

    @override_settings(SAML_ROUTE="sso/saml")
    def test_url_names_with_no_rl_slashes(self):
        self.assertEqual(reverse("saml2_auth"), "/sso/saml/")
        self.assertEqual(reverse("metadata"), "/sso/saml/metadata/")

    @override_settings(SAML_ROUTE="sso/saml")
    def test_url_resolving_with_no_rl_slashes(self):
        self.assertEqual(resolve("/sso/saml/").view_name, "saml2_auth")
        self.assertEqual(resolve("/sso/saml/metadata/").view_name, "metadata")
