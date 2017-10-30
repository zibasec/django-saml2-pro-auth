import re

from django.conf.urls import url
from django.conf import settings

from . import views

# pragma: no cover
SAML_ROUTE = settings.SAML_ROUTE
AUTH = r'^' + SAML_ROUTE + '$'
METADATA = r'^' + SAML_ROUTE + 'metadata/$'

urlpatterns = [
    url(AUTH, views.saml_login, name='saml2_auth'),
    url(METADATA, views.metadata, name='metadata'),
]
