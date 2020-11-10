import uuid

from django.urls import path, register_converter

from .models import SamlProvider
from .settings import app_settings
from .views import AcsView, MetadataView, SsoView

app_name = "saml2_pro_auth"


class ProviderConverter:
    regex = "[a-zA-Z0-9-]{4,36}"  # pylint: disable=anomalous-backslash-in-string

    def to_python(self, value):
        try:
            app_settings.SAML_PROVIDERS[value]
        except KeyError:
            try:
                SamlProvider.objects.get(pk=uuid.UUID(value))
            except (SamlProvider.DoesNotExist, ValueError) as err:
                raise ValueError from err

        return value

    def to_url(self, value):
        return value


register_converter(ProviderConverter, "samlp")


# Class based views
urlpatterns = [
    path("<samlp:provider>/acs/", AcsView.as_view(), name="acs"),
    path("<samlp:provider>/login/", SsoView.as_view(), name="login"),
    path(
        "<samlp:provider>/metadata/",
        MetadataView.as_view(),
        name="metadata",
    ),
]
