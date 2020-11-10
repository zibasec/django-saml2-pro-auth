from django.urls import path, register_converter

from .models import SamlProvider
from .settings import app_settings
from .views import AcsView, MetadataView, SsoView

SAML_ROUTE = f"{app_settings.SAML_ROUTE.strip('/')}"

app_name = "saml2_pro_auth"


class ProviderConverter:
    regex = "[a-zA-Z0-9]{3,16}"  # pylint: disable=anomalous-backslash-in-string

    def to_python(self, value):
        try:
            app_settings.SAML_PROVIDERS[value]
        except KeyError:
            try:
                SamlProvider.objects.get(provider_slug=value)
            except SamlProvider.DoesNotExist as err:
                raise ValueError from err

        return value

    def to_url(self, value):
        return value


register_converter(ProviderConverter, "samlp")


# Class based views
urlpatterns = [
    path(f"{SAML_ROUTE}/<samlp:provider>/acs/", AcsView.as_view(), name="acs"),
    path(f"{SAML_ROUTE}/<samlp:provider>/login/", SsoView.as_view(), name="login"),
    path(
        f"{SAML_ROUTE}/<samlp:provider>/metadata/",
        MetadataView.as_view(),
        name="metadata",
    ),
]
