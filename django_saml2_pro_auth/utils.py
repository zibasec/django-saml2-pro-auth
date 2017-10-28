from django.conf import settings

from onelogin.saml2.auth import OneLogin_Saml2_Auth


class SAMLError(Exception):
    pass

class SAMLSettingsError(Exception):
    pass


def strip_pem(string):
    """
    Take a pem formated file and return as a single string
    as required by python-saml
    """
    return string.replace('\n', '').replace('\r', '').lstrip('-----BEGIN CERTIFICATE-----').lstrip('-----BEGIN PRIVATE KEY-----').rstrip('-----END CERTIFICATE-----').lstrip('-----END PRIVATE KEY-----')

def get_provider_config(req):
    final_cfg = {}
    base_config = None
    try:
        provider = req['get_data']['provider']
    except KeyError:
        raise SAMLError("No provider specified in request")

    for index, provider in enumerate(settings.SAML_PROVIDERS):
        if provider.keys()[0] == provider:
            base_cfg = settings.SAML_PROVIDERS[index][provider]
            break

    if not base_config:
        raise SAMLSettingsError("Provider %s was not found in settings" % provider)

    final_cfg = base_cfg
    final_cfg['sp']['x509cert'] = strip_pem(final_cfg['sp']['x509cert'])
    final_cfg['sp']['privateKey'] = strip_pem(final_cfg['sp']['privateKey'])
    final_cfg['idp']['x509cert'] = strip_pem(final_cfg['idp']['x509cert'])

    return final_cfg


def init_saml_auth(req):
    provider_settings = get_provider_config(req)
    auth = OneLogin_Saml2_Auth(req, provider_settings)
    return auth

def prepare_django_request(request):
    # TODO: add settings.py support for HTTP_X_FORWADED
    # If server is behind proxys or balancers use the HTTP_X_FORWARDED fields
    result = {
        'https': 'on' if request.is_secure() else 'off',
        'http_host': request.META['HTTP_HOST'],
        'script_name': request.META['PATH_INFO'],
        'server_port': request.META['SERVER_PORT'],
        'get_data': request.GET.copy(),
        'post_data': request.POST.copy(),
        # TODO: add this as a config item for settings.py
        # Uncomment if using ADFS as IdP, https://github.com/onelogin/python-saml/pull/144
        # 'lowercase_urlencoding': True,
        'query_string': request.META['QUERY_STRING']
    }
    return result
