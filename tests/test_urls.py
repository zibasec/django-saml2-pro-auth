from django.test import TestCase
from django.test.utils import override_settings
from django.urls import resolve, reverse

import saml2_pro_auth.function_urls as function_urls
import saml2_pro_auth.urls as urls


class TestURLS(TestCase):
    def test_url_constants(self):
        self.assertEqual(urls.SAML_ROUTE, "saml")
        self.assertEqual(urls.METADATA, "saml/metadata/")

    def test_url_names_with_start_forward_slash(self):
        self.assertEqual(
            reverse("acs", kwargs={"provider": "testP"}), "/saml/acs/testP/"
        )
        self.assertEqual(
            reverse("sso", kwargs={"provider": "testP"}), "/saml/sso/testP/"
        )
        self.assertEqual(
            reverse("metadata", kwargs={"provider": "testP"}), "/saml/metadata/testP/"
        )

    def test_url_resolving_with_start_forward_slash(self):
        self.assertEqual(resolve("/saml/acs/classProvider/").view_name, "acs")
        self.assertEqual(resolve("/saml/sso/classProvider/").view_name, "sso")
        self.assertEqual(resolve("/saml/metadata/classProvider/").view_name, "metadata")


@override_settings(ROOT_URLCONF="saml2_pro_auth.function_urls")
class TestFuncURLS(TestCase):
    def test_url_constants(self):
        self.assertEqual(function_urls.SAML_ROUTE, "saml")
        self.assertEqual(function_urls.METADATA, "saml/metadata/")

    def test_url_names_with_start_forward_slash(self):
        self.assertEqual(reverse("saml2_auth"), "/saml/")
        self.assertEqual(reverse("metadata"), "/saml/metadata/")

    def test_url_resolving_with_start_forward_slash(self):
        self.assertEqual(resolve("/saml/").view_name, "saml2_auth")
        self.assertEqual(resolve("/saml/metadata/").view_name, "metadata")
