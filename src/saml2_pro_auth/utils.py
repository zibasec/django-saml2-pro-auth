from django.conf import settings
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils

from .settings import app_settings


class SAMLError(Exception):
    pass


class SAMLSettingsError(Exception):
    pass


def init_saml_auth(req):
    try:
        provider_settings = app_settings.SAML_PROVIDERS[req["get_data"]["provider"]]
    except KeyError:
        raise SAMLSettingsError("SAML_PROVIDERS is not defined in settings")

    req["lowercase_urlencoding"] = provider_settings.get("lowercase_urlencoding", False)
    req["idp_initiated_auth"] = provider_settings.get("idp_initiated_auth", True)
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
        "query_string": request.META["QUERY_STRING"],
    }

    if server_port:
        # Empty port will make a (lonely) colon ':' appear on the URL, so
        # it's better not to include it at all.
        results["server_port"] = server_port

    return results
