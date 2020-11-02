SECRET_KEY = "TESTSECRET"

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3"}}

ALLOWED_HOSTS = ["*"]

SAML_ROUTE = "/sso/saml"
ROOT_URLCONF = "django_saml2_pro_auth.urls"
