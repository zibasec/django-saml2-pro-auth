from django.conf import settings

class Settings:
    """
    A simple settings object that wraps Django settings
    """

    @property
    def SAML_ROUTE(self):
        return getattr(settings, "SAML_ROUTE", 'saml')

    @property
    def SAML_REDIRECT(self):
        return getattr(settings, "SAML_REDIRECT", '')

    @property
    def SAML_FAIL_REDIRECT(self):
        return getattr(settings, "SAML_FAIL_REDIRECT", getattr(settings, "LOGIN_REDIRECT_URL", "/"))

    @property
    def SAML_USERS_LOOKUP_ATTRIBUTE(self):
        return getattr(settings, "SAML_USERS_LOOKUP_ATTRIBUTE", 'username')

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


app_settings = Settings()
