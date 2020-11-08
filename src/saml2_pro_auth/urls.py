from django.urls import path, register_converter

from .settings import app_settings
from .views import AcsView, MetadataView, SsoView, metadata, saml_login

SAML_ROUTE = f"{app_settings.SAML_ROUTE.strip('/')}"
METADATA = f"{SAML_ROUTE}/metadata/"

app_name = "saml2_pro_auth"


class ProviderConverter:
    regex = "[\w-]+"  # pylint: disable=anomalous-backslash-in-string

    def to_python(self, value):
        try:
            return {value: app_settings.SAML_PROVIDERS[value]}
        except KeyError:
            raise ValueError

    def to_url(self, value):
        return value


register_converter(ProviderConverter, "samlp")


# Class based views
urlpatterns = [
    path(f"{SAML_ROUTE}/acs/<samlp:provider>/", AcsView.as_view(), name="acs"),
    path(f"{SAML_ROUTE}/sso/<samlp:provider>/", SsoView.as_view(), name="sso"),
    path(
        f"{SAML_ROUTE}/metadata/<samlp:provider>/",
        MetadataView.as_view(),
        name="metadata",
    ),
]
