# NameID Formats from the SAML Core 2.0 spec (8.3 Name Identifier Format Identifiers)
UNSPECIFIED = "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified"
EMAIL = "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"
PERSISTENT = "urn:oasis:names:tc:SAML:2.0:nameid-format:persistent"
TRANSIENT = "urn:oasis:names:tc:SAML:2.0:nameid-format:transient"
X509SUBJECT = "urn:oasis:names:tc:SAML:1.1:nameid-format:X509SubjectName"
WINDOWS = "urn:oasis:names:tc:SAML:1.1:nameid-format:WindowsDomainQualifiedName"
KERBEROS = "urn:oasis:names:tc:SAML:2.0:nameid-format:kerberos"
ENTITY = "urn:oasis:names:tc:SAML:2.0:nameid-format:entity"

# Tuples of NameID Formats strings and friendly names for use in choices.
NAMEID_FORMAT_CHOICES = [
    (UNSPECIFIED, "Unspecified"),
    (EMAIL, "EmailAddress"),
    (PERSISTENT, "Persistent"),
    (TRANSIENT, "Transient"),
    (X509SUBJECT, "X509SubjectName"),
    (WINDOWS, "WindowsDomainQualifiedName"),
    (KERBEROS, "Kerberos"),
    (ENTITY, "Entity"),
]

# Protocol Bindings
HTTP_POST_BINDING = "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
HTTP_REDIRECT_BINDING = "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
SAML_PROTOCOL_BINDINGS = [
    (HTTP_POST_BINDING, "HTTP-POST"),
    (HTTP_REDIRECT_BINDING, "HTTP-Redirect"),
]
