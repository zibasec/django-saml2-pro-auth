import re

#from django.conf.urls import url
from django.urls import re_path
from django.conf import settings

from . import views

SAML_ROUTE = getattr(settings, 'SAML_ROUTE', 'sso/saml')

if SAML_ROUTE.strip()[-1] == '/':
    SAML_ROUTE = SAML_ROUTE.rstrip('/')

if SAML_ROUTE.strip()[0] == '/':
    SAML_ROUTE = SAML_ROUTE.lstrip('/')

AUTH = r'^' + SAML_ROUTE + '/$'
METADATA = r'^' + SAML_ROUTE + '/metadata/$'

urlpatterns = [
    re_path(AUTH, views.saml_login, name='saml2_auth'),
    re_path(METADATA, views.metadata, name='metadata'),
]
