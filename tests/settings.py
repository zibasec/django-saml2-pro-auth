from pathlib import Path

from .data.configs import MOCK_SAML2_CONFIG

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "TESTSECRET"

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "saml2_pro_auth",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(BASE_DIR / "db.sqlite3"),
    }
}

ALLOWED_HOSTS = ["*"]

ROOT_URLCONF = "tests.urls"

SAML_PROVIDERS = MOCK_SAML2_CONFIG
