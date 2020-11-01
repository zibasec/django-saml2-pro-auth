import os

MOCK_SAML2_CONFIG = [
    {
        "MyProvider": {
            "strict": True,
            "debug": True,
            "sp": {
                "entityId": "https://example.com/sso/saml/metadata?provider=MyProvider",
                "assertionConsumerService": {
                    "url": "https://example.com/sso/saml/?acs&amp;provider=MyProvider",
                    "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
                },
                "singleLogoutService": {
                    "url": "https://example.com/sso/saml/?sls&amp;provider=MyProvider",
                    "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
                },
                "NameIDFormat": "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified",
                "x509cert": open("tests/mock_certs/sp.crt", "r").read(),
                "privateKey": open("tests/mock_certs/sp.key", "r").read(),
            },
            "idp": {
                "entityId": "https://myprovider.example.com/0f3172cf",
                "singleSignOnService": {
                    "url": "https://myprovider.example.com/applogin/appKey/0f3172cf/customerId/AA333",
                    "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
                },
                "singleLogoutService": {
                    "url": "https://myprovider.example.com/applogout",
                    "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
                },
                "x509cert": open("tests/mock_certs/myprovider.crt", "r").read(),
            },
            "organization": {
                "en-US": {
                    "name": "example inc",
                    "displayname": "Example Incorporated",
                    "url": "example.com",
                }
            },
            "contact_person": {
                "technical": {
                    "given_name": "Jane Doe",
                    "email_address": "jdoe@examp.com",
                },
                "support": {
                    "given_name": "Jane Doe",
                    "email_address": "jdoe@examp.com",
                },
            },
            "security": {
                "name_id_encrypted": False,
                "authn_requests_signed": True,
                "logout_requests_signed": False,
                "logout_response_signed": False,
                "sign_metadata": False,
                "want_messages_signed": False,
                "want_assertions_signed": True,
                "want_name_id": True,
                "want_name_id_encrypted": False,
                "want_assertions_encrypted": True,
                "signature_algorithm": "http://www.w3.org/2000/09/xmldsig#rsa-sha1",
                "digest_algorithm": "http://www.w3.org/2000/09/xmldsig#rsa-sha1",
            },
        }
    }
]
