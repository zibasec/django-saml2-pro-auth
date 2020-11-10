from typing import Tuple

from onelogin.saml2.auth import OneLogin_Saml2_Auth

from .models import SamlProvider
from .settings import app_settings


class SAMLError(Exception):
    """
    Used to indicate errors during SAML request/response processing
    """


class SAMLSettingsError(Exception):
    """
    Used to indicate errors in the SAML settings
    """


def init_saml_auth(
    request, provider_name: str
) -> Tuple[OneLogin_Saml2_Auth, dict, dict]:
    """
    Gets the SAML provider settings and returns a prepared SAML request and OneLogin Auth object
    """
    saml_req = prepare_django_request(request)
    provider_settings, user_map = get_provider_settings(saml_req, provider_name)
    saml_req["lowercase_urlencoding"] = provider_settings.get(
        "lowercase_urlencoding", False
    )
    saml_req["idp_initiated_auth"] = provider_settings.get("idp_initiated_auth", True)
    auth = OneLogin_Saml2_Auth(saml_req, provider_settings)
    return auth, saml_req, user_map


def prepare_django_request(request) -> dict:
    """
    Prepares the saml request object from the Django request
    """
    if app_settings.SAML_OVERRIDE_HOSTNAME:
        http_host = app_settings.SAML_OVERRIDE_HOSTNAME
    else:
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


def get_provider_settings(req: dict, provider_name: str) -> Tuple[dict, dict]:
    """
    Returns the provider settings
    """
    try:
        provider_settings = app_settings.SAML_PROVIDERS[provider_name]
        user_map = app_settings.SAML_USERS_MAP.get(provider_name, dict())
    except KeyError:
        try:
            samlp = SamlProvider.objects.get(provider_slug=provider_name)
            provider_settings = samlp.get_provider_config(
                app_settings.SAML_PROVIDER_CONFIG_TEMPLATE
            )
            user_map = samlp.attributes
        except SamlProvider.DoesNotExist as err:
            raise SAMLSettingsError(
                "SAML_PROVIDERS is not defined in settings"
            ) from err

    urls = build_sp_urls(req, provider_name)
    # TODO: Skip if already defined in config
    provider_settings["sp"]["entityId"] = urls["entityId"]
    provider_settings["sp"]["assertionConsumerService"]["url"] = urls["acs_url"]
    return provider_settings, user_map


def build_sp_urls(req: dict, provider_name: str) -> dict:
    """
    Builds and returns the SP entity ID and acs URLs.
    TODO: Should eventually be expanded to return the SLS/SLO URLs as well.
    """
    protocol = "https" if req["https"] == "on" else "http"

    path = f"{app_settings.SAML_ROUTE.strip('/')}/{provider_name}"
    base_url = f"{protocol}://{req['http_host']}/{path}/"
    acs_url = f"{base_url}acs/"
    return {
        "entityId": base_url,
        "acs_url": acs_url,
    }
