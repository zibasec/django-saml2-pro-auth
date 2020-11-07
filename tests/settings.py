from .data.configs import MOCK_SAML2_CONFIG

SECRET_KEY = "TESTSECRET"

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3"}}

ALLOWED_HOSTS = ["*"]

SAML_ROUTE = "/saml/"
ROOT_URLCONF = "saml2_pro_auth.urls"

SAML_PROVIDERS = MOCK_SAML2_CONFIG