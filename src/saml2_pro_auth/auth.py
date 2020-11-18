from datetime import datetime, timezone

from django.contrib.auth import get_user_model
from django.core.cache import caches

from .settings import app_settings
from .utils import SAMLError, SAMLSettingsError


def get_clean_map(user_map: dict, saml_data: dict) -> dict:
    final_map = dict()
    strict_mapping = app_settings.SAML_USERS_STRICT_MAPPING
    for usr_k, usr_v in user_map.items():
        if strict_mapping and isinstance(usr_v, dict):
            if "default" in usr_v.keys():
                raise SAMLSettingsError(
                    "A default value is set for key %s in SAML_USER_MAP \
                    while SAML_USERS_STRICT_MAPPING is activated"
                    % usr_k
                )

        index = 0
        val = usr_v
        default = None
        if isinstance(usr_v, dict):
            index = usr_v.get("index", 0)
            val = usr_v.get("key", usr_k)
            default = usr_v.get("default", None)

        attr = saml_data.get(val, default)
        if isinstance(attr, list):
            attr = attr[index]

        if attr is None:
            if strict_mapping:
                raise SAMLError(
                    "Response missing attribute %s while SAML_USERS_STRICT_MAPPING is activated"
                    % usr_k
                )

            continue

        final_map[usr_k] = attr

    return final_map


class Backend:  # pragma: no cover
    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False. Custom user models that don't have
        that attribute are allowed.
        """
        is_active = getattr(user, "is_active", None)
        return is_active or is_active is None

    def authenticate(self, request, saml_auth=None, user_map=dict()):
        if not saml_auth:
            return None

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

        final_map = get_clean_map(user_map, saml_auth.get_attributes())

        lookup_attr = app_settings.SAML_USERS_LOOKUP_ATTRIBUTE
        lookup_map = dict()
        if isinstance(lookup_attr, str):
            lookup_map = {lookup_attr: saml_auth.get_nameid()}
        elif isinstance(lookup_attr, (tuple, list)):
            if lookup_attr[1] == "NameId":
                lookup_map = {lookup_attr[0]: saml_auth.get_nameid()}
            else:
                lookup_map = {lookup_attr[0]: final_map[lookup_attr[1]]}
        else:
            raise SAMLSettingsError(
                "The value of SAML_USERS_LOOKUP_ATTRIBUTE must be a str, tuple, or list"
            )

        sync_attributes = app_settings.SAML_USERS_SYNC_ATTRIBUTES
        create_users = app_settings.SAML_AUTO_CREATE_USERS

        try:
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
                    try:
                        user.update(**final_map)
                    except Exception:
                        pass
        except Exception as err:
            return None

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
