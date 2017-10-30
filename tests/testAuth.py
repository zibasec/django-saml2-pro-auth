import unittest
from django.test.utils import override_settings
from django.conf import settings
from django.test import RequestFactory
from django_saml2_pro_auth.auth import get_clean_map, get_provider_index

class TestAuthFns(unittest.TestCase):
    settings.configure()

    @override_settings(SAML_PROVIDERS=[{'MyProvider': dict()},{'2ndProvider': dict()}])
    def test_get_provider_index1(self):
        r1_factory = RequestFactory()
        request1 = r1_factory.get('/sso/saml/?provider=MyProvider')
        provider1, index1 = get_provider_index(request1)
        self.assertEqual(provider1, 'MyProvider')
        self.assertEqual(index1, 0)

    @override_settings(SAML_PROVIDERS=[{'MyProvider': dict()},{'2ndProvider': dict()}])
    def test_get_provider_index2(self):
        r2_factory = RequestFactory()
        request2 = r2_factory.get('/sso/saml/?provider=2ndProvider')
        provider2, index2 = get_provider_index(request2)
        self.assertEqual(provider2, '2ndProvider')
        self.assertEqual(index2, 1)

    def test_mapping_users_with_index_values(self):
        user_map = {
            'email': {
                'index': 0,
                'key': 'Email'
            },
            'name': {
                'index': 0,
                'key': 'Username'
            }
        }

        saml_map = {
            'Username': ['montypython'],
            'lastName': ['Cleese'],
            'Email': ['montypython@example.com'],
            'firstName': ['John']
        }

        merged_map = get_clean_map(user_map, saml_map)
        self.assertEqual(merged_map['email'], 'montypython@example.com')
        self.assertEqual(merged_map['name'], 'montypython')

    def test_mapping_users_without_index_values(self):
        user_map = {
            'email': 'Email',
            'name': 'Username'
        }

        saml_map = {
            'Username': 'montypython',
            'lastName': 'Cleese',
            'Email': 'montypython@example.com',
            'firstName': 'John'
        }

        merged_map = get_clean_map(user_map, saml_map)
        self.assertEqual(merged_map['email'], 'montypython@example.com')
        self.assertEqual(merged_map['name'], 'montypython')

    def test_mapping_users_without_mixed_value_styles(self):
        user_map = {
            'email': 'Email',
            'name': {
                'index': 1,
                'key': 'Username'
            }
        }

        saml_map = {
            'Username': ['','montypython'],
            'lastName': 'Cleese',
            'Email': 'montypython@example.com',
            'firstName': 'John'
        }

        merged_map = get_clean_map(user_map, saml_map)
        self.assertEqual(merged_map['email'], 'montypython@example.com')
        self.assertEqual(merged_map['name'], 'montypython')
