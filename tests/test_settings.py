from django.test import SimpleTestCase
from django.test.utils import override_settings

from saml2_pro_auth.settings import app_settings


class SettingsTests(SimpleTestCase):
    @override_settings(SAML_ROUTE="foo")
    def test_can_override(self):
        self.assertEqual(app_settings.SAML_ROUTE, "foo")
