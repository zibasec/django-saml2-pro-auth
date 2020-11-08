from django.urls import path

from .settings import app_settings
from .views import metadata, saml_login

SAML_ROUTE = f"{app_settings.SAML_ROUTE.strip('/')}"
METADATA = f"{SAML_ROUTE}/metadata/"

app_name = "saml2_pro_auth"

# Legacy function views
urlpatterns = [
    path(f"{SAML_ROUTE}/", saml_login, name="saml2_auth"),
    path(f"{SAML_ROUTE}/metadata/", metadata, name="metadata"),
]
