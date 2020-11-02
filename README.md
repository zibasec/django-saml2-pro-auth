# Django SAML2 Pro Auth

SAML2 authentication backend for Django

---

[![build-status-badge]][build-status]
[![pypi-version-badge]][pypi]
[![license-badge]][license]

[![pypi-pyverions-badge]][pypi]
[![pypi-djverions-badge]][pypi]
[![downloads-badge]][downloads]

## Requirements

- Python (3.6, 3.7, 3.8, 3.9)
- Django (2.2, 3.0, 3.1)
- python3-saml (>=1.9.0)

We **recommend** and only support patched versions of Python and Django that are still receiving updates.

## Installation

`pip install django-saml2-pro-auth`

### Prerequisites

The [python3-saml] package depends on the [xmlsec] package which requires the installation of native C libraries on your OS of choice.

You will want to follow the instructions for setting up the native dependencies on your OS of choice.

## Configuration

### Django Settings

Here is an example full configuration. Scroll down to read about each option

```python

AUTHENTICATION_BACKENDS = [
      'django_saml2_pro_auth.auth.Backend'
]

SAML_ROUTE = 'sso/saml/'

SAML_REDIRECT = '/'

SAML_FAIL_REDIRECT = '/login_failed'

SAML_USERS_MAP = [{
    "MyProvider" : {
      "email": dict(key="Email", index=0),
      "name": dict(key="Username", index=0)
    }

}]


SAML_PROVIDERS = [{
    "MyProvider": {
        "strict": True,
        "debug": False,
        "custom_base_path": "",
        "sp": {
            "entityId": "https://test.davila.io/sso/saml/metadata",
            "assertionConsumerService": {
                "url": "https://test.davila.io/sso/saml/?acs",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
            },
            "singleLogoutService": {
                "url": "https://test.davila.io/sso/saml/?sls",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
            },
            "NameIDFormat": "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified",
            ## For the cert/key you can place their content in
            ## the x509cert and privateKey params
            ## as single-line strings or place them in
            ## certs/sp.key and certs/sp.crt or you can supply a
            ## path via custom_base_path which should contain
            ## sp.crt and sp.key
            "x509cert": "",
            "privateKey": "",
        },
        "idp": {
            "entityId": "https://kdkdfjdfsklj.my.MyProvider.com/0f3172cf-5aa6-40f4-8023-baf9d0996cec",
            "singleSignOnService": {
                "url": "https://kdkdfjdfsklj.my.MyProvider.com/applogin/appKey/0f3172cf-5aa6-40f4-8023-baf9d0996cec/customerId/kdkdfjdfsklj",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
            },
            "singleLogoutService": {
                "url": "https://kdkdfjdfsklj.my.MyProvider.com/applogout",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
            },
            "x509cert": open(os.path.join(BASE_DIR,'certs/MyProvider.crt'), 'r').read(),
        },
        "organization": {
            "en-US": {
                "name": "example inc",
                "displayname": "Example Incorporated",
                "url": "example.com"
            }
        },
        "contact_person": {
            "technical": {
                "given_name": "Jane Doe",
                "email_address": "jdoe@examp.com"
            },
            "support": {
                "given_name": "Jane Doe",
                "email_address": "jdoe@examp.com"
            }
        },
        "security": {
            "nameIdEncrypted": False,
            "authnRequestsSigned": True,
            "logoutRequestSigned": False,
            "logoutResponseSigned": False,
            "signMetadata": False,
            "wantMessagesSigned": False,
            "wantAssertionsSigned": True,
            "wantNameId": True,
            "wantNameIdEncrypted": False,
            "wantAssertionsEncrypted": True,
            "signatureAlgorithm": "http://www.w3.org/2000/09/xmldsig#rsa-sha1",
            "digestAlgorithm": "http://www.w3.org/2000/09/xmldsig#rsa-sha1",
        }

    }
}]
```

**AUTHENTICATION_BACKENDS:** This is required exactly as in the example. It tells Django to use this as a valid auth mechanism.

**SAML_ROUTE (optional, default=/sso/saml/):** This tells Django where to do all SAML related activities. The default route is /sso/saml/. You still need to include the source urls in your own `urls.py`. For example:

```python
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
import profiles.urls
import accounts.urls
import django_saml2_pro_auth.urls as saml_urls

from . import views

urlpatterns = [
    url(r'^$', views.HomePage.as_view(), name='home'),
    url(r'^about/$', views.AboutPage.as_view(), name='about'),
    url(r'^users/', include(profiles.urls, namespace='profiles')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include(accounts.urls, namespace='accounts')),
    url(r'^', include(saml_urls, namespace='saml')),
]

```

So first import the urls via `import django_saml2_pro_auth.urls as saml_urls` (it's up to you if you want name it or not). Then add it to your patterns via `url(r'^', include(saml_urls, namespace='saml'))`. This example will give you the default routes that this auth backend provides.

**SAML_REDIRECT (optional, default=None):** This tells the auth backend where to redirect users after they've logged in via the IdP. **NOTE**: This is not needed for _most_ users. Order of precedence is: SAML_REDIRECT value (if defined), RELAY_STATE provided in the SAML response, and the fallback is simply to go to the root path of your application.

**SAML_FAIL_REDIRECT (optional, default=None):** This tells the auth backend where to redirect when the SAML authentication fails on the Django side. When using the supplied backend this can happen when a user is marked with is_active=False in the Django DB while still being able to authenticate with the IdP. When SAML_FAIl_REDIRECT has not been set, a SAMLError is raised to avoid redirect loops.

**SAML_USERS_MAP (required):** This is what makes it possible to map the attributes as they come from your IdP into attributes that are part of your User model in Django. There a few ways you can define this. The dict keys (the left-side) are the attributes as defined in YOUR User model, the dict values (the right-side) are the attributes as supplied by your IdP.

```python
## Simplest Approach, when the SAML attributes supplied by the IdP are just plain strings
## This means my User model has an 'email' and 'name' attribute while my IdP passes 'Email' and 'Username' attrs
SAML_USERS_MAP = [{
    "myIdp" : {
      "email": "Email",
      "name": "Username
    }
}]
```

Sometimes, IdPs might provide values as Arrays (even when it really should just be a string). This package supports that too. For example, suppose your IdP supplied user attributes with the following data structure:
`{"Email": ["foo@example.com"], "Username": "foo"}`
You simply would make the key slightly more complex where `key` is the key and `index` represents the index where the desired value is located. See below:

```python
SAML_USERS_MAP = [{
    "myIdp" : {
      "email": {"key": "Email", "index": 0},
      "name": "Username
    }
```

And of course, you can use the dict structure even when there IdP supplied attribute isn't an array. For example:

```python
SAML_USERS_MAP = [{
    "myIdp" : {
      "email": {"key": "Email"},
      "name": {"key": "Username"}
    }
```

**SAML_USERS_LOOKUP_ATTRIBUTE (optional):**
Specifies the User model field to be used for object lookup in the database.
Has to be one of the dict keys for the Django's User model specified in "SAML_USERS_MAP".

The attribute in the Django User model should have the "unique" flag set.
(In the default User model in django only username has a unique contstraint in the DB, the same email could be used by multiple users)

Defaults to "username"

```python
SAML_USERS_LOOKUP_ATTRIBUTE = "email"
```

**SAML_USERS_SYNC_ATTRIBUTES (optional):**
Specifies if the user attributes have to be updated at each login with those received from the IdP.

Defaults to False

```python
SAML_USERS_SYNC_ATTRIBUTES = True
```

**SAML_USERS_STRICT_MAPPING (optional):**
Specifies if every user attribute defined in SAML_USER_MAP must be present
in the saml response or not.

Defaults to True

```python
SAML_USERS_STRICT_MAPPING = False
```

If set to False, you can optionally specify a default value in the "SAML_USER_MAP"
dict and it will set the value when the attribute is not present in the IdP response object.

Example default value setting

```python
# set default value for is_superuser and is_staff to False
SAML_USERS_STRICT_MAPPING = False
SAML_USERS_MAP = [{
    "MyProvider" : {
      "email": dict(key="email", index=0),
      "username": dict(key="username", index=0),
      "is_superuser": dict(key="is_superuser", index=0, default=False),
      "is_staff": dict(key="is_staff", index=0, default=False)
    }
}]
```

**SAML_PROVIDERS:** This is exactly the same spec as OneLogin's [python-saml and python3-saml packages](https://github.com/onelogin/python3-saml#settings). The big difference is here you supply a list of dicts where the top most key(s) must map 1:1 to the top most keys in `SAML_USERS_MAP`. Also, this package allows you to ref the cert/key files via `open()` calls. This is to allow those of you with multiple external customers to login to your platform with any N number of IdPs.

## Routes

| **Route**                                 | **Uses**                                                                                                                                                                                                              |
|-------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `/sso/saml/?acs&amp;provider=MyProvider`     | The Assertion Consumer Service Endpoint. This is where your IdP will be POSTing assertions. The 'provider' query string must have a value that matches a top level key of your SAML_PROVIDERS settings.               |
| `/sso/saml/metadata?provider=MyProvider` | This is where the SP (ie your Django App) has metadata. Some IdPs request this to generate configuration. The 'provider' query string must have a value that matches a top level key of your SAML_PROVIDERS settings. |
| `/sso/saml/?provider=MyProvider`         | Use this endpoint when you want to trigger an SP-initiated login. For example, this could be the `href`of a "Login with ClientX Okta" button.                                                                         |

## Gotchas

The following are things that you may run into issue with. Here are some tips.

- Ensure the value of the SP `entityId` config matches up with what you supply in your IdPs configuration.
- Your IdP may default to particular Signature type, usually `Assertion` or `Response` are the options. Depending on how you define your SAML provider config, it will dictate what this value should be.

## Wishlist and TODOs

The following are things that arent present yet but would be cool to have

- Implement logic for Single Logout Service
- ADFS IdP support
- Integration test with full on mock saml interactions to test the actual backend auth
- Tests add coverage to views and the authenticate() get_user() methods in the auth backend
- models (with multi-tentant support) for idp and sp in order to facilitate management via django admin
- Tests/Support for Django 2

## Release Process

The following release process is manual for now but may be integrated into a CI action in the future.

All code contributions are merged to the main branch through a standard pull request, test, review, merge process. At certain intervals new releases should be cut and pushed to PyPI. This is the standard process for creating new releases from the main branch.

1. Update the version information in `setup.cfg` e.g., `version = X.Y.Z`
1. Create a new `git` tag with the same version 

    ```sh
    git tag -a -s vX.Y.Z -m 'Version X.Y.Z'
    ```

    - `-s` requires you to have GPG and signing properly setup.
1. Push the tags to the remote

    ```sh
    git push --follow-tags origin vX.Y.Z
    ```

1. Create the source and binary distributions and upload to PyPI.

    ```sh
    # runs
    # python setup.py sdist bdist_wheel
    # twine check dist/*
    tox -f build
    # upload to test pypi
    twine upload testpypi dist/django_saml2_pro_auth-X.Y.Z-*
    # upload to production pypi
    twine upload dist/django_saml2_pro_auth-X.Y.Z-*
    ```

1. Create a release on GitHub

**TODO** Add a proper CHANGELOG to release process.

[build-status]: https://github.com/zibasec/django-saml2-pro-auth/actions?query=workflow%3Abuild-and-test+branch%3Amaster
[build-status-badge]: https://img.shields.io/github/workflow/status/zibasec/django-saml2-pro-auth/build-and-test/master
[license]: https://raw.githubusercontent.com/zibasec/django-saml2-pro-auth/master/LICENSE
[license-badge]: https://img.shields.io/github/license/zibasec/django-saml2-pro-auth
[pypi]: https://pypi.org/project/django-saml2-pro-auth/
[pypi-version-badge]: https://img.shields.io/pypi/v/django-saml2-pro-auth.svg
[pypi-pyverions-badge]: https://img.shields.io/pypi/pyversions/django-saml2-pro-auth.svg
[pypi-djverions-badge]: https://img.shields.io/pypi/djversions/django-saml2-pro-auth.svg
[downloads]: https://pepy.tech/project/django-saml2-pro-auth
[downloads-badge]: https://pepy.tech/badge/django-saml2-pro-auth
[python3-saml]: https://github.com/onelogin/python3-saml
[xmlsec]: https://pypi.org/project/xmlsec/
