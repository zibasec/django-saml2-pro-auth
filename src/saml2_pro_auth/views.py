from django.contrib.auth import REDIRECT_FIELD_NAME, authenticate, login
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from onelogin.saml2.errors import OneLogin_Saml2_Error
from onelogin.saml2.utils import OneLogin_Saml2_Utils

from .settings import app_settings
from .utils import SAMLError, SAMLSettingsError, init_saml_auth


class SamlBadRequest(SuspiciousOperation):
    pass


class GenericSamlView(View):
    def dispatch(self, request, *args, **kwargs):
        """Initialize attributes shared by all view methods."""
        try:
            auth, req, user_map = init_saml_auth(request, kwargs["provider"])
        except (SAMLError, SAMLSettingsError, KeyError) as err:
            raise SAMLError("Invalid request or provider settings") from err

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
        except OneLogin_Saml2_Error as err:
            raise SAMLError("Invalid SP metadata") from err

        errors = saml_settings.validate_metadata(metadata_doc)

        if errors:
            raise SAMLError(", ".join(errors))

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
            raise SamlBadRequest("Bad Request")

        auth.process_response(request_id=request_id)
        errors = auth.get_errors()

        if not errors:
            user = authenticate(
                request=request,
                saml_auth=auth,
                user_map=user_map,
            )
            if user is not None:
                try:
                    login(request, user)
                except (ValueError, TypeError):
                    error_reason = "Bad Request"
                    if auth.get_settings().is_debug_active():
                        error_reason = "Login Failed"
                    raise SamlBadRequest("%s" % error_reason)

                # Only write data into the session if everything is successful
                # and the user is logged in
                request.session["samlUserdata"] = auth.get_attributes()
                request.session["samlNameId"] = auth.get_nameid()
                request.session["samlSessionIndex"] = auth.get_session_index()
                relay_state = req["post_data"].get("RelayState", app_settings.SAML_REDIRECT) or "/"
                if relay_state and OneLogin_Saml2_Utils.get_self_url(req) != relay_state:
                    response = redirect(
                        auth.redirect_to(relay_state)
                    )
                else:
                    response = redirect(OneLogin_Saml2_Utils.get_self_url(req))
            else:
                error_reason = "Bad Request"
                if auth.get_settings().is_debug_active():
                    error_reason = "User lookup Failed"
                raise SamlBadRequest("%s" % error_reason)

        else:
            error_reason = "Bad Request"
            if auth.get_settings().is_debug_active():
                error_reason = auth.get_last_error_reason()
            raise SamlBadRequest("%s" % error_reason)

        response.delete_cookie("sp_auth")
        return response


class SsoView(GenericSamlView):
    http_method_names = ["get", "head"]

    def get(self, request, *args, **kwargs):
        # SP-SSO start request
        auth = kwargs["saml_auth"]
        req = kwargs["saml_req"]
        return_to = req["get_data"].get(REDIRECT_FIELD_NAME, app_settings.SAML_REDIRECT) or "/"
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
