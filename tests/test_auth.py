from django.test import RequestFactory, TestCase
from django.test.utils import override_settings

from django_saml2_pro_auth.auth import get_clean_map, get_provider_index
from django_saml2_pro_auth.utils import SAMLError, SAMLSettingsError


class TestAuth(TestCase):
    @override_settings(SAML_PROVIDERS=[{"MyProvider": dict()}, {"2ndProvider": dict()}])
    def test_get_provider_index1(self):
        r1_factory = RequestFactory()
        request1 = r1_factory.get("/sso/saml/?provider=MyProvider")
        provider1, index1 = get_provider_index(request1)
        self.assertEqual(provider1, "MyProvider")
        self.assertEqual(index1, 0)

    @override_settings(SAML_PROVIDERS=[{"MyProvider": dict()}, {"2ndProvider": dict()}])
    def test_get_provider_index2(self):
        r2_factory = RequestFactory()
        request2 = r2_factory.get("/sso/saml/?provider=2ndProvider")
        provider2, index2 = get_provider_index(request2)
        self.assertEqual(provider2, "2ndProvider")
        self.assertEqual(index2, 1)

    @override_settings(SAML_PROVIDERS=[{"MyProvider": {"name": "MyProvider"}}])
    def test_get_provider_index_missing_query_str(self):
        r2_factory = RequestFactory()
        request2 = r2_factory.get("/sso/saml/")
        provider, _ = get_provider_index(request2)
        self.assertEqual(provider, "MyProvider")

    @override_settings(SAML_PROVIDERS=[{"MyProvider": dict()}, {"2ndProvider": dict()}])
    def test_get_provider_index_not_in_settings(self):
        r2_factory = RequestFactory()
        request2 = r2_factory.get("/sso/saml/?provider=BadProvider")
        self.assertRaises(SAMLError, get_provider_index, request2)

    def test_mapping_users_with_index_values(self):
        user_map = {
            "email": {"index": 0, "key": "Email"},
            "name": {"index": 0, "key": "Username"},
        }

        saml_map = {
            "Username": ["montypython"],
            "lastName": ["Cleese"],
            "Email": ["montypython@example.com"],
            "firstName": ["John"],
        }

        merged_map = get_clean_map(user_map, saml_map)
        self.assertEqual(merged_map["email"], "montypython@example.com")
        self.assertEqual(merged_map["name"], "montypython")

    def test_mapping_users_without_index_values(self):
        user_map = {"email": "Email", "name": "Username"}

        saml_map = {
            "Username": "montypython",
            "lastName": "Cleese",
            "Email": "montypython@example.com",
            "firstName": "John",
        }

        merged_map = get_clean_map(user_map, saml_map)
        self.assertEqual(merged_map["email"], "montypython@example.com")
        self.assertEqual(merged_map["name"], "montypython")

    def test_mapping_users_with_mixed_value_styles(self):
        user_map = {
            "email": "Email",
            "name": {"index": 1, "key": "Username"},
            "customer": {"key": "Client"},
        }

        saml_map = {
            "Username": ["", "montypython"],
            "lastName": "Cleese",
            "Email": "montypython@example.com",
            "firstName": "John",
            "Client": "examplecorp",
        }

        merged_map = get_clean_map(user_map, saml_map)
        self.assertEqual(merged_map["email"], "montypython@example.com")
        self.assertEqual(merged_map["name"], "montypython")
        self.assertEqual(merged_map["customer"], "examplecorp")

    def test_mapping_users_with_default_values(self):
        user_map = {
            "email": "Email",
            "name": {"index": 1, "key": "Username", "default": "testUsername"},
            "customer": {"key": "Client", "default": "testClient"},
        }

        saml_map = {
            "Username": ["", "montypython"],
            "lastName": "Cleese",
            "Email": "montypython@example.com",
            "firstName": "John",
            "Client": "examplecorp",
        }

        self.assertRaises(SAMLSettingsError, get_clean_map, user_map, saml_map)

    @override_settings(SAML_USERS_STRICT_MAPPING=False)
    def test_non_strict_mapping_users_with_index_values(self):
        user_map = {
            "email": {"index": 0, "key": "Email"},
            "name": {"index": 0, "key": "Username"},
            "age": {"index": 0, "key": "Age"},
        }

        saml_map = {
            "Username": ["montypython"],
            "lastName": ["Cleese"],
            "Email": ["montypython@example.com"],
            "firstName": ["John"],
        }

        merged_map = get_clean_map(user_map, saml_map)
        self.assertEqual(merged_map["email"], "montypython@example.com")
        self.assertEqual(merged_map["name"], "montypython")
        self.assertIsNone(merged_map["age"])

    @override_settings(SAML_USERS_STRICT_MAPPING=False)
    def test_non_strict_mapping_users_without_index_values(self):
        user_map = {
            "email": "Email",
            "name": "Username",
            "age": "Age",
        }

        saml_map = {
            "Username": "montypython",
            "lastName": "Cleese",
            "Email": "montypython@example.com",
            "firstName": "John",
        }

        merged_map = get_clean_map(user_map, saml_map)
        self.assertEqual(merged_map["email"], "montypython@example.com")
        self.assertEqual(merged_map["name"], "montypython")
        self.assertIsNone(merged_map["age"])

    @override_settings(SAML_USERS_STRICT_MAPPING=False)
    def test_non_strict_mapping_users_with_mixed_value_styles(self):
        user_map = {
            "email": "Email",
            "name": {"index": 1, "key": "Username"},
            "customer": {"key": "Client"},
            "age": "Age",
        }

        saml_map = {
            "Username": ["", "montypython"],
            "lastName": "Cleese",
            "Email": "montypython@example.com",
            "firstName": "John",
            "Client": "examplecorp",
        }

        merged_map = get_clean_map(user_map, saml_map)
        self.assertEqual(merged_map["email"], "montypython@example.com")
        self.assertEqual(merged_map["name"], "montypython")
        self.assertEqual(merged_map["customer"], "examplecorp")
        self.assertIsNone(merged_map["age"])

    @override_settings(SAML_USERS_STRICT_MAPPING=False)
    def test_non_strict_mapping_users_with_default_value(self):
        user_map = {
            "email": {"key": "Email"},
            "name": {"key": "Username", "index": 1},
            "is_superuser": {"key": "is_superuser", "default": False},
            "is_staff": {"key": "is_staff", "default": True},
        }

        saml_map = {
            "Username": ["", "montypython"],
            "lastName": "Cleese",
            "Email": "montypython@example.com",
            "firstName": "John",
            "Client": "examplecorp",
        }

        merged_map = get_clean_map(user_map, saml_map)
        self.assertEqual(merged_map["email"], "montypython@example.com")
        self.assertEqual(merged_map["name"], "montypython")
        self.assertEqual(merged_map["is_superuser"], False)
        self.assertEqual(merged_map["is_staff"], True)
