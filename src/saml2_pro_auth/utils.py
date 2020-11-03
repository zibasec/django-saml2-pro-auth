from django.conf import settings
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils


class SAMLError(Exception):
    pass


class SAMLSettingsError(Exception):
    pass


def get_provider_config(req):
    final_cfg = {}
    base_cfg = None
    try:
        providers = settings.SAML_PROVIDERS
    except AttributeError:
        raise SAMLSettingsError("SAML_PROVIDERS is not defined in settings")
    try:
        provider = req["get_data"]["provider"]
    except KeyError:
        provider = list(providers[0].keys())[0]
        req["get_data"]["provider"] = provider

    for index, provider_obj in enumerate(providers):
        if list(provider_obj.keys())[0] == provider:
            base_cfg = settings.SAML_PROVIDERS[index][provider]
            break

    if not base_cfg:
        raise SAMLSettingsError("Provider %s was not found in settings" % provider)

    final_cfg = base_cfg
    try:
        final_cfg["sp"]["x509cert"] = OneLogin_Saml2_Utils.format_cert(
            final_cfg["sp"]["x509cert"]
        )
        final_cfg["sp"]["privateKey"] = OneLogin_Saml2_Utils.format_private_key(
            final_cfg["sp"]["privateKey"]
        )
        final_cfg["idp"]["x509cert"] = OneLogin_Saml2_Utils.format_cert(
            final_cfg["idp"]["x509cert"]
        )
    except KeyError:
        pass

    return final_cfg


def init_saml_auth(req):
    provider_settings = get_provider_config(req)
    auth = OneLogin_Saml2_Auth(req, provider_settings)
    return auth


def prepare_django_request(request):
    http_host = request.get_host()

    if "HTTP_X_FORWARDED_FOR" in request.META:
        server_port = None
        https = request.META.get("HTTP_X_FORWARDED_PROTO") == "https"
    else:
        server_port = request.META.get("SERVER_PORT")
        https = request.is_secure()

    results = {
        "https": "on" if https else "off",
        "http_host": http_host,
        "script_name": request.META["PATH_INFO"],
        "get_data": request.GET.copy(),
        "post_data": request.POST.copy(),
        "query_string": request.META["QUERY_STRING"]
        # TODO: add this as a config item for settings.py
        # Uncomment if using ADFS as IdP, https://github.com/onelogin/python-saml/pull/144
        # 'lowercase_urlencoding': True,
    }

    if server_port:
        # Empty port will make a (lonely) colon ':' appear on the URL, so
        # it's better not to include it at all.
        results["server_port"] = server_port

    return results
