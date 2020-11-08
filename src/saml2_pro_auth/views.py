from django.contrib.auth import REDIRECT_FIELD_NAME, authenticate, login
from django.core.cache import caches
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.errors import OneLogin_Saml2_Error
from onelogin.saml2.utils import OneLogin_Saml2_Utils

from .settings import app_settings
from .utils import SAMLError, SAMLSettingsError, init_saml_auth, prepare_django_request


class BaseSamlView(View):
    def dispatch(self, request, *args, **kwargs):
        """Initialize attributes shared by all view methods."""
        try:
            name, settings = [i for i in kwargs["provider"].items()][0]
            req = prepare_django_request(request)
            req["lowercase_urlencoding"] = settings.get("lowercase_urlencoding", False)
            auth = OneLogin_Saml2_Auth(req, settings)

        except (SAMLError, SAMLSettingsError, KeyError):
            return HttpResponseServerError("Invalid request or provider settings")

        self.saml_auth = auth
        self.saml_req = req
        self.provider_name = name
        self.allow_idp_initiated_auth = settings.get("idp_initiated_auth", True)
        return super().dispatch(request, *args, **kwargs)


class MetadataView(BaseSamlView):
    http_method_names = ["get", "head"]

    def get(self, request, *args, **kwargs):
        saml_settings = self.saml_auth.get_settings()
        try:
            metadata = saml_settings.get_sp_metadata()
        except OneLogin_Saml2_Error:
            return HttpResponseServerError("Invalid SP metadata")

        errors = saml_settings.validate_metadata(metadata)

        if errors:
            return HttpResponseServerError(content=", ".join(errors))

        return HttpResponse(content=metadata, content_type="text/xml")


@method_decorator(csrf_exempt, name="dispatch")
class AcsView(BaseSamlView):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        request_id = request.get_signed_cookie(
            "sp_auth", default=None, salt="saml2_pro_auth.authnrequestid", max_age=300
        )
        if not self.allow_idp_initiated_auth and request_id is None:
            return HttpResponseBadRequest("Bad Request")

        self.saml_auth.process_response(request_id=request_id)
        errors = self.saml_auth.get_errors()

        if not errors:
            user = authenticate(
                request=request, provider=self.provider_name, saml_auth=self.saml_auth
            )
            if user is not None:
                login(request, user)

                if app_settings.SAML_REDIRECT:
                    response = redirect(app_settings.SAML_REDIRECT)
                elif (
                    "RelayState" in self.saml_req["post_data"]
                    and OneLogin_Saml2_Utils.get_self_url(self.saml_req)
                    != self.saml_req["post_data"]["RelayState"]
                ):
                    response = redirect(
                        self.saml_auth.redirect_to(
                            self.saml_req["post_data"]["RelayState"]
                        )
                    )
                else:
                    response = redirect(
                        OneLogin_Saml2_Utils.get_self_url(self.saml_req)
                    )
            else:
                request.session.flush()
                response = redirect(app_settings.SAML_FAIL_REDIRECT)

        else:
            error_reason = "Bad Request"
            if self.saml_auth.get_settings().is_debug_active():
                error_reason = self.saml_auth.get_last_error_reason()
            response = HttpResponseBadRequest("%s" % error_reason)

        response.delete_cookie("sp_auth")
        return response


class SsoView(BaseSamlView):
    http_method_names = ["get", "head"]

    def get(self, request, *args, **kwargs):
        # SP-SSO start request
        return_to = app_settings.SAML_REDIRECT or self.saml_req["get_data"].get(
            REDIRECT_FIELD_NAME, ""
        )
        saml_request = self.saml_auth.login(return_to=return_to)
        response = redirect(saml_request)
        response.set_signed_cookie(
            "sp_auth",
            self.saml_auth.get_last_request_id(),
            salt="saml2_pro_auth.authnrequestid",
            max_age=300,
            secure=self.saml_req["https"] == "on",
            httponly=True,
            samesite=None,
        )
        return response


@csrf_exempt
def saml_login(request):
    try:
        req = prepare_django_request(request)
        auth = init_saml_auth(req)
    except (SAMLError, SAMLSettingsError):
        return HttpResponseServerError("Something went wrong.")

    # SP initiated flow start
    if "sso" in req["get_data"] and "provider" in req["get_data"]:
        return_to = app_settings.SAML_REDIRECT or req["get_data"].get(
            REDIRECT_FIELD_NAME, ""
        )
        saml_request = auth.login(return_to=return_to)
        response = redirect(saml_request)
        response.set_signed_cookie(
            "sp_auth",
            auth.get_last_request_id(),
            salt="saml2_pro_auth.authnrequestid",
            max_age=300,
            secure=req["https"] == "on",
            httponly=True,
            samesite=None,
        )
        return response

    # IDP initiated flow or SP initiated response
    if "acs" in req["get_data"] and "provider" in req["get_data"]:
        request_id = request.session.pop("AuthNRequestID", None)
        auth.process_response(request_id=request_id)
        errors = auth.get_errors()

        if not errors:
            user = authenticate(
                request=request, provider=req["get_data"]["provider"], saml_auth=auth
            )
            if user is not None:
                login(request, user)
                if app_settings.SAML_REDIRECT:
                    response = redirect(app_settings.SAML_REDIRECT)
                elif (
                    "RelayState" in req["post_data"]
                    and OneLogin_Saml2_Utils.get_self_url(req)
                    != req["post_data"]["RelayState"]
                ):
                    response = redirect(
                        auth.redirect_to(req["post_data"]["RelayState"])
                    )
                else:
                    response = redirect(OneLogin_Saml2_Utils.get_self_url(req))
            else:
                request.session.flush()
                response = redirect(app_settings.SAML_FAIL_REDIRECT)
        else:
            error_reason = "Bad Request"
            if auth.get_settings().is_debug_active():
                error_reason = auth.get_last_error_reason()
            response = HttpResponseBadRequest("%s" % error_reason)

        response.delete_cookie("sp_auth")
        return response

    # Improper view redirect to fail url
    return HttpResponseBadRequest("Bad Request")


def metadata(request):
    try:
        req = prepare_django_request(request)
        auth = init_saml_auth(req)
    except (SAMLError, SAMLSettingsError):
        return HttpResponseServerError("Something went wrong.")

    saml_settings = auth.get_settings()
    metadata = saml_settings.get_sp_metadata()
    errors = saml_settings.validate_metadata(metadata)

    if len(errors) == 0:
        resp = HttpResponse(content=metadata, content_type="text/xml")
    else:
        resp = HttpResponseServerError(content=", ".join(errors))
    return resp
