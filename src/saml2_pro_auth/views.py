from django.contrib.auth import REDIRECT_FIELD_NAME, authenticate, login
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from onelogin.saml2.errors import OneLogin_Saml2_Error
from onelogin.saml2.utils import OneLogin_Saml2_Utils

from .settings import app_settings
from .utils import SAMLError, SAMLSettingsError, init_saml_auth, prepare_django_request


class GenericSamlView(View):
    def dispatch(self, request, *args, **kwargs):
        """Initialize attributes shared by all view methods."""
        try:
            auth, req, user_map = init_saml_auth(request, kwargs["provider"])
        except (SAMLError, SAMLSettingsError, KeyError):
            return HttpResponseServerError("Invalid request or provider settings")

        kwargs["saml_auth"] = auth
        kwargs["saml_req"] = req
        kwargs["user_map"] = user_map
        return super().dispatch(request, *args, **kwargs)


class MetadataView(GenericSamlView):
    http_method_names = ["get", "head"]

    def get(self, request, *args, **kwargs):
        saml_settings = kwargs["saml_auth"].get_settings()
        try:
            metadata_doc = saml_settings.get_sp_metadata()
        except OneLogin_Saml2_Error:
            return HttpResponseServerError("Invalid SP metadata")

        errors = saml_settings.validate_metadata(metadata_doc)

        if errors:
            return HttpResponseServerError(content=", ".join(errors))

        return HttpResponse(content=metadata_doc, content_type="text/xml")


@method_decorator(csrf_exempt, name="dispatch")
class AcsView(GenericSamlView):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        auth = kwargs["saml_auth"]
        req = kwargs["saml_req"]
        user_map = kwargs["user_map"]
        request_id = request.get_signed_cookie(
            "sp_auth", default=None, salt="saml2_pro_auth.authnrequestid", max_age=300
        )
        if not req["idp_initiated_auth"] and request_id is None:
            return HttpResponseBadRequest("Bad Request")

        auth.process_response(request_id=request_id)
        errors = auth.get_errors()

        if not errors:
            user = authenticate(
                request=request,
                saml_auth=auth,
                user_map=user_map,
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


class SsoView(GenericSamlView):
    http_method_names = ["get", "head"]

    def get(self, request, *args, **kwargs):
        # SP-SSO start request
        auth = kwargs["saml_auth"]
        req = kwargs["saml_req"]
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
