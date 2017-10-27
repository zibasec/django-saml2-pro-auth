from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseServerError)

from onelogin.saml2.auth import OneLogin_Saml2_Auth


class Backend(object):

    def authenticate(self, request):
        if not request.session['samlSessionIndex'] or not request.session['samlUserdata']:
            return None

        User = get_user_model()
        email = request.session['samlUserdata']['Email'][0]
        usr_args = dict(username=email, email=email)
        user, _ = User.objects.get_or_create(**usr_args)
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
