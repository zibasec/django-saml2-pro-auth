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
    base_cfg = None
    try:
        provider = req['get_data']['provider']
    except KeyError:
        raise SAMLError("No provider specified in request")

    for index, provider_obj in enumerate(settings.SAML_PROVIDERS):
        if provider_obj.keys()[0] == provider:
            base_cfg = settings.SAML_PROVIDERS[index][provider]
            break

    if not base_cfg:
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
    http_host = request.META.get('HTTP_HOST', None)

    if 'HTTP_X_FORWARDED_FOR' in request.META:
        server_port = None
        https = request.META.get('HTTP_X_FORWARDED_PROTO') == 'https'
    else:
        server_port = request.META.get('SERVER_PORT')
        https = request.is_secure()

    results = {
        'https': 'on' if https else 'off',
        'http_host': http_host,
        'script_name': request.META['PATH_INFO'],
        'get_data': request.GET.copy(),
        'post_data': request.POST.copy(),
        'query_string': request.META['QUERY_STRING']
        # TODO: add this as a config item for settings.py
        # Uncomment if using ADFS as IdP, https://github.com/onelogin/python-saml/pull/144
        # 'lowercase_urlencoding': True,
    }

    if server_port:
        # Empty port will make a (lonely) colon ':' appear on the URL, so
        # it's better not to include it at all.
        results['server_port'] = server_port

    return results
