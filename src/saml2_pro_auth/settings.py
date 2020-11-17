from django.conf import settings

PROVIDER_CONFIG_TEMPLATE = {
    "strict": True,
    "sp": {
        "x509cert": "",
        "privateKey": "",
    },
    # No one actually sets these fields in their metadata
    # "organization": {
    #     "en-US": {
    #         "name": "",
    #         "displayname": "",
    #         "url": "",
    #     }
    # },
    # "contactPerson": {
    #     "technical": {"givenName": "", "emailAddress": ""},
    #     "support": {"givenName": "", "emailAddress": ""},
    # },
    "security": {
        "nameIdEncrypted": False,
        "authnRequestsSigned": True,
        "logoutRequestSigned": True,
        "logoutResponseSigned": True,
        "signMetadata": True,
        "wantMessagesSigned": True,
        "wantAssertionsSigned": False,
        "wantAssertionsEncrypted": False,
        "wantNameId": True,
        "wantNameIdEncrypted": False,
        "wantAttributeStatement": False,
        "signatureAlgorithm": "http://www.w3.org/2000/09/xmldsig#rsa-sha256",
        "digestAlgorithm": "http://www.w3.org/2001/04/xmlenc#sha256",
    },
}


class Settings:
    """
    A simple settings object that wraps Django settings
    """

    @property
    def SAML_REDIRECT(self):
        return getattr(settings, "SAML_REDIRECT", "/")

    @property
    def SAML_USERS_LOOKUP_ATTRIBUTE(self):
        return getattr(settings, "SAML_USERS_LOOKUP_ATTRIBUTE", ("username", "NameId"))

    @property
    def SAML_USERS_SYNC_ATTRIBUTES(self):
        return getattr(settings, "SAML_USERS_SYNC_ATTRIBUTES", False)

    @property
    def SAML_USERS_STRICT_MAPPING(self):
        return getattr(settings, "SAML_USERS_STRICT_MAPPING", True)

    @property
    def SAML_PROVIDERS(self):
        return getattr(settings, "SAML_PROVIDERS", dict())

    @property
    def SAML_PROVIDER_CONFIG_TEMPLATE(self):
        return getattr(
            settings, "SAML_PROVIDER_CONFIG_TEMPLATE", PROVIDER_CONFIG_TEMPLATE
        )

    @property
    def SAML_USERS_MAP(self):
        return getattr(settings, "SAML_USERS_MAP", dict())

    @property
    def SAML_AUTO_CREATE_USERS(self):
        return getattr(settings, "SAML_AUTO_CREATE_USERS", True)

    @property
    def SAML_CACHE(self):
        return getattr(settings, "SAML_CACHE", "default")

    @property
    def SAML_REPLAY_PROTECTION(self):
        return getattr(settings, "SAML_REPLAY_PROTECTION", True)

    @property
    def SAML_OVERRIDE_HOSTNAME(self):
        return getattr(settings, "SAML_OVERRIDE_HOSTNAME", "")


app_settings = Settings()
