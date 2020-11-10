import uuid
from copy import deepcopy

from django.conf import settings
from django.db import models

try:
    from django.db.models import JSONField
except ImportError:
    if "sqlite" in settings.DATABASES["default"]["ENGINE"]:
        from .json_field import JSONField
    else:
        from django.contrib.postgres.fields import JSONField

from .constants import (
    HTTP_POST_BINDING,
    NAMEID_FORMAT_CHOICES,
    SAML_PROTOCOL_BINDINGS,
    UNSPECIFIED,
)


class SamlProvider(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        "Name",
        help_text="A descriptive name for the provider configuration.",
        max_length=50,
        blank=False,
    )
    idp_issuer = models.TextField(
        "IdP Issuer (Entity ID)",
        help_text="The Issuer or Entity ID from your Identity Provider.",
        blank=False,
        max_length=1024,
    )
    idp_x509 = models.TextField(
        "IdP Certificate",
        help_text="A PEM encoded public certificate provided by your Identity Provider.",
        blank=False,
    )
    idp_sso_url = models.TextField(
        "IdP Single Sign-On URL",
        help_text="The single sign-on service URL provided by your IdP.",
        blank=False,
        max_length=2048,
    )
    idp_sso_binding = models.CharField(
        "IdP Single Sign-On Binding",
        help_text="The single sign-on service protocol binding set by your IdP. HTTP-POST is recommended.",
        choices=SAML_PROTOCOL_BINDINGS,
        default=HTTP_POST_BINDING,
        blank=False,
        max_length=255,
    )
    nameidformat = models.CharField(
        "NameID Format",
        help_text="Format of the assertions subject statement NameID attribute. This must match the format sent from your IdP.",
        choices=NAMEID_FORMAT_CHOICES,
        default=UNSPECIFIED,
        blank=False,
        max_length=255,
    )
    sp_acs_binding = models.TextField(
        "SP Single Sign-On Binding",
        help_text="The single sign-on service protocol binding for this service provider. HTTP-POST is recommended.",
        choices=SAML_PROTOCOL_BINDINGS,
        default=HTTP_POST_BINDING,
        blank=False,
        max_length=1024,
    )
    debug = models.BooleanField(
        "Debug", help_text="Enable settings debug messages.", default=False
    )
    lowercase_urlencoding = models.BooleanField(
        "Support ADFS",
        help_text="Enable ADFS lowercase Url encoding support.",
        default=False,
    )
    idp_initiated_auth = models.BooleanField(
        "Allow IdP Initiated Assertions",
        help_text="Accept unsolicited IdP initiated assertions.",
        default=False,
    )
    sec_want_messages_signed = models.BooleanField(
        "Signed Responses",
        help_text="Require signed responses from the IdP.",
        default=True,
    )
    sec_want_assertions_signed = models.BooleanField(
        "Signed Assertions",
        help_text="Require signed assertions from the IdP.",
        default=False,
    )
    sec_want_assertions_encrypted = models.BooleanField(
        "Encrypted Assertions",
        help_text="Require encrypted assertions from the IdP.",
        default=False,
    )
    attributes = JSONField(
        "Attribute Statements",
        help_text="Map attributes from the IdP to User fields.",
        default=dict,
        blank=True,
    )

    def __str__(self):

        return self.name

    def get_provider_config(self, defaults):
        """
        Interprolate settings from model into config
        """
        config = deepcopy(defaults)
        config = dict(
            idp=dict(
                entityId=self.idp_issuer,
                x509cert=self.idp_x509,
                singleSignOnService=dict(
                    url=self.idp_sso_url,
                    binding=self.idp_sso_binding,
                ),
            ),
            sp={
                **config.setdefault("sp", dict()),
                **{
                    "entityId": "",
                    "NameIDFormat": self.nameidformat,
                    "assertionConsumerService": dict(
                        url="",
                        binding=self.sp_acs_binding,
                    ),
                },
            },
            security={
                **config.setdefault("security", dict()),
                **{
                    "wantMessagesSigned": self.sec_want_messages_signed,
                    "wantAssertionsSigned": self.sec_want_assertions_signed,
                    "wantAssertionsEncrypted": self.sec_want_assertions_encrypted,
                },
            },
        )
        config["debug"] = self.debug
        config["lowercase_urlencoding"] = self.lowercase_urlencoding
        config["idp_initiated_auth"] = self.idp_initiated_auth

        return config
