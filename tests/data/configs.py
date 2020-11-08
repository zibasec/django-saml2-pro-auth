MOCK_SAML2_CONFIG = {
    "functionProvider": {
        "strict": True,
        "debug": True,
        "sp": {
            "entityId": "https://example.com/sso/saml/metadata?provider=functionProvider",
            "assertionConsumerService": {
                "url": "https://example.com/sso/saml/?acs&amp;provider=functionProvider",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
            },
            "singleLogoutService": {
                "url": "https://example.com/sso/saml/?sls&amp;provider=functionProvider",
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
        "contactPerson": {
            "technical": {"givenName": "Jane Doe", "emailAddress": "jdoe@examp.com"},
            "support": {"givenName": "Jane Doe", "emailAddress": "jdoe@examp.com"},
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
            "digestAlgorithm": "http://www.w3.org/2001/04/xmlenc#sha256",
        },
    },
    "classProvider": {
        "strict": True,
        "debug": True,
        "lowercase_urlencoding": False,
        "idp_initiated_auth": True,
        "sp": {
            "entityId": "https://example.com/saml/metadata/classProvider/",
            "assertionConsumerService": {
                "url": "https://example.com/saml/acs/classProvider/",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
            },
            "singleLogoutService": {
                "url": "https://example.com/saml/sls/classProvider/",
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
        "contactPerson": {
            "technical": {"givenName": "Jane Doe", "emailAddress": "jdoe@examp.com"},
            "support": {"givenName": "Jane Doe", "emailAddress": "jdoe@examp.com"},
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
            "digestAlgorithm": "http://www.w3.org/2001/04/xmlenc#sha256",
        },
    },
}
