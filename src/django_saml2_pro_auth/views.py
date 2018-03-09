from django.conf import settings
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseServerError)
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, REDIRECT_FIELD_NAME

from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.settings import OneLogin_Saml2_Settings
from onelogin.saml2.utils import OneLogin_Saml2_Utils

from .utils import SAMLError, SAMLSettingsError
from .utils import (get_provider_config,
                    init_saml_auth, prepare_django_request)




@csrf_exempt
def saml_login(request):
    attributes = None
    req = prepare_django_request(request)
    auth = init_saml_auth(req)

    if 'acs' in req['get_data']:
        # IDP initiated
        request_id = None

        if 'AuthNRequestID' in request.session:
            request_id = request.session['AuthNRequestID']

        auth.process_response(request_id=request_id)
        errors = auth.get_errors()
        not_auth_warn = not auth.is_authenticated()

        if not errors:
            if 'AuthNRequestID' in request.session:
                del request.session['AuthNRequestID']

            request.session['samlUserdata'] = auth.get_attributes()
            request.session['samlNameId'] = auth.get_nameid()
            request.session['samlSessionIndex'] = auth.get_session_index()
            attributes = request.session['samlUserdata'].items()
            user = authenticate(request=request)
            login(request, user)
            if hasattr(settings, 'SAML_REDIRECT'):
                return HttpResponseRedirect(settings.SAML_REDIRECT)
            elif 'RelayState' in req['post_data'] and OneLogin_Saml2_Utils.get_self_url(req) != req['post_data']['RelayState']:
                return HttpResponseRedirect(auth.redirect_to(req['post_data']['RelayState']))
            else:
                return HttpResponseRedirect(OneLogin_Saml2_Utils.get_self_url(req))
        else:
            raise SAMLError('ERRORS FOUND IN SAML REQUEST: %s' % errors)
    elif 'provider' in req['get_data']:
        # SP Initiated
        if hasattr(settings, 'SAML_REDIRECT'):
            return HttpResponseRedirect(auth.login(return_to=settings.SAML_REDIRECT))
        elif REDIRECT_FIELD_NAME in req['get_data']:
            return HttpResponseRedirect(auth.login(return_to=req['get_data'][REDIRECT_FIELD_NAME]))
        elif 'RelayState' in req['post_data']:
                return HttpResponseRedirect(auth.redirect_to(req['post_data']['RelayState']))
        else:
            redir = OneLogin_Saml2_Utils.get_self_url(req)
            return HttpResponseRedirect(auth.login(return_to=redir))
    else:
        return HttpResponseRedirect(auth.login())

def metadata(request):
    req = prepare_django_request(request)
    auth = init_saml_auth(req)
    saml_settings = auth.get_settings()
    metadata = saml_settings.get_sp_metadata()
    errors = saml_settings.validate_metadata(metadata)

    if len(errors) == 0:
        resp = HttpResponse(content=metadata, content_type='text/xml')
    else:
        resp = HttpResponseServerError(content=', '.join(errors))
    return resp
