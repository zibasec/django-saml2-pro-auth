from django.test import TestCase
from django.test.utils import override_settings

from saml2_pro_auth.auth import get_clean_map
from saml2_pro_auth.utils import SAMLSettingsError


class TestAuth(TestCase):
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
            "Username": ["montypython"],
            "lastName": ["Cleese"],
            "Email": ["montypython@example.com"],
            "firstName": ["John"],
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
            "lastName": ["Cleese"],
            "Email": ["montypython@example.com"],
            "firstName": ["John"],
            "Client": ["examplecorp"],
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
            "lastName": ["Cleese"],
            "Email": ["montypython@example.com"],
            "firstName": ["John"],
            "Client": ["examplecorp"],
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
        self.assertTrue("age" not in merged_map)

    @override_settings(SAML_USERS_STRICT_MAPPING=False)
    def test_non_strict_mapping_users_without_index_values(self):
        user_map = {
            "email": "Email",
            "name": "Username",
            "age": "Age",
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
        self.assertTrue("age" not in merged_map)

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
            "lastName": ["Cleese"],
            "Email": ["montypython@example.com"],
            "firstName": ["John"],
            "Client": ["examplecorp"],
        }

        merged_map = get_clean_map(user_map, saml_map)
        self.assertEqual(merged_map["email"], "montypython@example.com")
        self.assertEqual(merged_map["name"], "montypython")
        self.assertEqual(merged_map["customer"], "examplecorp")
        self.assertTrue("age" not in merged_map)

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
            "lastName": ["Cleese"],
            "Email": ["montypython@example.com"],
            "firstName": ["John"],
            "Client": ["examplecorp"],
        }

        merged_map = get_clean_map(user_map, saml_map)
        self.assertEqual(merged_map["email"], "montypython@example.com")
        self.assertEqual(merged_map["name"], "montypython")
        self.assertEqual(merged_map["is_superuser"], False)
        self.assertEqual(merged_map["is_staff"], True)
