from datetime import datetime, timezone

from django.contrib.auth import get_user_model
from django.core.cache import caches

from .settings import app_settings
from .utils import SAMLSettingsError


def get_clean_map(user_map: dict, saml_data: dict, nameid: str = "") -> dict:
    final_map = dict()
    strict_mapping = app_settings.SAML_USERS_STRICT_MAPPING
    for usr_k, usr_v in user_map.items():
        if strict_mapping:
            if isinstance(usr_v, dict):
                if "default" in usr_v.keys():
                    raise SAMLSettingsError(
                        "A default value is set for key %s in SAML_USER_MAP while SAML_USERS_STRICT_MAPPING is activated"
                        % usr_k
                    )
                if "index" in usr_v.keys():
                    final_map[usr_k] = saml_data[usr_v["key"]][usr_v["index"]]
                else:
                    final_map[usr_k] = saml_data[usr_v["key"]][0]
            else:
                final_map[usr_k] = saml_data[user_map[usr_k]][0]
        else:
            if isinstance(usr_v, dict):
                if "index" in usr_v:
                    final_map[usr_k] = (
                        saml_data[usr_v["key"]][usr_v["index"]]
                        if usr_v["key"] in saml_data
                        else usr_v["default"]
                        if "default" in usr_v.keys()
                        else None
                    )
                else:
                    final_map[usr_k] = (
                        saml_data[usr_v["key"]][0]
                        if usr_v["key"] in saml_data
                        else usr_v["default"]
                        if "default" in usr_v.keys()
                        else None
                    )
            else:
                final_map[usr_k] = (
                    saml_data[user_map[usr_k]][0]
                    if user_map[usr_k] in saml_data
                    else None
                )

    final_map["NameId"] = nameid
    return final_map


class Backend:  # pragma: no cover
    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False. Custom user models that don't have
        that attribute are allowed.
        """
        is_active = getattr(user, "is_active", None)
        return is_active or is_active is None

    def authenticate(self, request, provider=None, saml_auth=None, user_map=dict()):
        if not provider or not saml_auth:
            return None

        request.session["samlUserdata"] = saml_auth.get_attributes()
        request.session["samlNameId"] = saml_auth.get_nameid()
        request.session["samlSessionIndex"] = saml_auth.get_session_index()
        assertion_id = saml_auth.get_last_assertion_id()
        not_on_or_after = datetime.fromtimestamp(
            saml_auth.get_last_assertion_not_on_or_after(), tz=timezone.utc
        )
        assertion_timeout = not_on_or_after - datetime.now(tz=timezone.utc)

        if app_settings.SAML_REPLAY_PROTECTION:
            # Store the assertion id in cache so we can ensure only once
            # processing during validity period
            cache = caches[app_settings.SAML_CACHE]
            if not cache.add(
                assertion_id, assertion_id, timeout=assertion_timeout.seconds
            ):
                # Check if adding the key worked, if the return is false the key already exists
                # so we fail auth. This should let us only process an assertion ID once
                return None

        UserModel = get_user_model()

        final_map = get_clean_map(
            user_map, request.session["samlUserdata"], request.session["samlNameId"]
        )

        lookup_map = app_settings.SAML_USERS_LOOKUP_ATTRIBUTE
        if isinstance(lookup_map, str):
            lookup_map = {lookup_map: final_map["NameId"]}
        elif isinstance(lookup_map, tuple):
            lookup_map = {lookup_map[0]: final_map[lookup_map[1]]}

        sync_attributes = app_settings.SAML_USERS_SYNC_ATTRIBUTES
        create_users = app_settings.SAML_AUTO_CREATE_USERS

        # lookup_map = lookup_attribute # {lookup_attribute: final_map[lookup_attribute_name]}

        if create_users and sync_attributes:
            user, _ = UserModel._default_manager.update_or_create(
                defaults=final_map, **lookup_map
            )
        elif create_users:
            user, _ = UserModel._default_manager.get_or_create(
                defaults=final_map, **lookup_map
            )
        else:
            user = UserModel._default_manager.get(**lookup_map)
            if sync_attributes:
                user.update(**final_map)

        if self.user_can_authenticate(user):
            return user

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            user = UserModel._default_manager.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None

        return user if self.user_can_authenticate(user) else None


SamlBackend = Backend
