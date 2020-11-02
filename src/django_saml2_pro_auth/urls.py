try:
    from django.urls import re_path as url
except ImportError:
    from django.conf.urls import url

from django.conf import settings

from . import views

app_name = "django_saml2_pro_auth"

SAML_ROUTE = getattr(settings, "SAML_ROUTE", "sso/saml")

if SAML_ROUTE.strip()[-1] == "/":
    SAML_ROUTE = SAML_ROUTE.rstrip("/")

if SAML_ROUTE.strip()[0] == "/":
    SAML_ROUTE = SAML_ROUTE.lstrip("/")

AUTH = r"^" + SAML_ROUTE + "/$"
METADATA = r"^" + SAML_ROUTE + "/metadata/$"

urlpatterns = [
    url(AUTH, views.saml_login, name="saml2_auth"),
    url(METADATA, views.metadata, name="metadata"),
]
