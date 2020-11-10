from django.test import TestCase

from saml2_pro_auth.models import SamlProvider
from saml2_pro_auth.settings import PROVIDER_CONFIG_TEMPLATE


class SamlProviderModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        SamlProvider.objects.create(
            name="TestProvider",
            idp_issuer="FakeIssuer",
            idp_x509="NOTACERT",
            idp_sso_url="https://some.random.url/idp/",
        )

    def test_object_name_is_name(self):
        provider = SamlProvider.objects.get(name="TestProvider")
        self.assertEqual(provider.name, str(provider))

    def test_get_provider_config(self):
        provider = SamlProvider.objects.get(name="TestProvider")
        config = provider.get_provider_config(PROVIDER_CONFIG_TEMPLATE)
        self.assertEqual(config["idp"]["entityId"], provider.idp_issuer)
        self.assertEqual(
            config["idp"]["singleSignOnService"]["url"], provider.idp_sso_url
        )
        self.assertEqual(
            config["idp"]["singleSignOnService"]["binding"], provider.idp_sso_binding
        )
        self.assertEqual(config["idp"]["x509cert"], provider.idp_x509)
        self.assertEqual(config["sp"]["NameIDFormat"], provider.nameidformat)
        self.assertEqual(
            config["sp"]["assertionConsumerService"]["binding"], provider.sp_acs_binding
        )
        self.assertEqual(
            config["security"]["wantMessagesSigned"], provider.sec_want_messages_signed
        )
        self.assertEqual(
            config["security"]["wantAssertionsSigned"],
            provider.sec_want_assertions_signed,
        )
        self.assertEqual(
            config["security"]["wantAssertionsEncrypted"],
            provider.sec_want_assertions_encrypted,
        )
