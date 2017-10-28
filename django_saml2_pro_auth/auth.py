from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseServerError)

from onelogin.saml2.auth import OneLogin_Saml2_Auth

from .utils import SAMLError, prepare_django_request

User = get_user_model()

def get_provider_index(request):
    """Helper to get the saml config index of a provider in order to grab
    the proper user map"""
    req = prepare_django_request(request)
    try:
        provider = req['get_data']['provider']
    except KeyError:
        raise SAMLError("No provider specified in request")

    for index, provider in enumerate(settings.SAML_PROVIDERS):
        if provider.keys()[0] == provider:
            return provider, index

    raise SAMLError("The provider: %s was not found in settings.py" % provider)

class Backend(object):

    def authenticate(self, request):
        if not request.session['samlSessionIndex'] or not request.session['samlUserdata']:
            return None

        provider, provider_index = get_provider_index(request)
        user_map = settings.SAML_USERS_MAP[provider_index][provider]
        user, _ = User.objects.get_or_create(**user_map)
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
