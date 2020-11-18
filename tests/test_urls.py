from django.test import TestCase
from django.urls import resolve, reverse

import saml2_pro_auth.urls as urls


class TestURLS(TestCase):
    def test_url_names_with_start_forward_slash(self):
        self.assertEqual(
            reverse("saml2_pro_auth:acs", kwargs={"provider": "testP"}),
            "/sso/saml/testP/acs/",
        )
        self.assertEqual(
            reverse("saml2_pro_auth:login", kwargs={"provider": "testP"}),
            "/sso/saml/testP/login/",
        )
        self.assertEqual(
            reverse("saml2_pro_auth:metadata", kwargs={"provider": "testP"}),
            "/sso/saml/testP/metadata/",
        )

    def test_url_resolving_with_start_forward_slash(self):
        self.assertEqual(
            resolve("/sso/saml/classProvider/acs/").view_name, "saml2_pro_auth:acs"
        )
        self.assertEqual(
            resolve("/sso/saml/classProvider/login/").view_name, "saml2_pro_auth:login"
        )
        self.assertEqual(
            resolve("/sso/saml/classProvider/metadata/").view_name,
            "saml2_pro_auth:metadata",
        )
