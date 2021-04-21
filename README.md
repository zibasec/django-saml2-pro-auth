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
- Django (2.2.20, 3.0.14, 3.1.8)
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
      'saml2_pro_auth.auth.Backend'
]

SAML_REDIRECT = '/'

SAML_USERS_MAP = {
    "MyProvider" : {
      "email": dict(key="Email", index=0),
      "name": dict(key="Username", index=0)
    }
}


SAML_PROVIDERS = {
    "MyProvider": {
        "strict": True,
        "debug": False,
        "custom_base_path": "", # Optional, set if you are reading files from a custom location on disk
        "lowercase_urlencoding": False, # This can be set to True to enable ADFS compatibility
        "idp_initiated_auth": True, # This can be set to False to disable IdP-initiated auth
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
        "contactPerson": {
            "technical": {
                "givenName": "Jane Doe",
                "emailAddress": "jdoe@examp.com"
            },
            "support": {
                "givenName": "Jane Doe",
                "emailAddress": "jdoe@examp.com"
            }
        },
        "security": {
            "nameIdEncrypted": False,
            "authnRequestsSigned": True,
            "logoutRequestSigned": False,
            "logoutResponseSigned": False,
            "signMetadata": True,
            "wantMessagesSigned": True,
            "wantAssertionsSigned": True,
            "wantAssertionsEncrypted": True,
            "wantNameId": True,
            "wantNameIdEncrypted": False,
            "wantAttributeStatement": True,
            # Algorithm that the toolkit will use on signing process. Options:
            #    'http://www.w3.org/2000/09/xmldsig#rsa-sha1'
            #    'http://www.w3.org/2000/09/xmldsig#dsa-sha1'
            #    'http://www.w3.org/2001/04/xmldsig-more#rsa-sha256'
            #    'http://www.w3.org/2001/04/xmldsig-more#rsa-sha384'
            #    'http://www.w3.org/2001/04/xmldsig-more#rsa-sha512'
            "signatureAlgorithm": "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256",

            # Algorithm that the toolkit will use on digest process. Options:
            #    'http://www.w3.org/2000/09/xmldsig#sha1'
            #    'http://www.w3.org/2001/04/xmlenc#sha256'
            #    'http://www.w3.org/2001/04/xmldsig-more#sha384'
            #    'http://www.w3.org/2001/04/xmlenc#sha512'
            'digestAlgorithm': "http://www.w3.org/2001/04/xmlenc#sha256"
        }

    }
}
```

**AUTHENTICATION_BACKENDS:** This is required exactly as in the example. It tells Django to use this as a valid auth mechanism.

**SAML_ROUTE (optional, default=/sso/saml/):** This tells Django where to do all SAML related activities. The default route is `/saml/`. You still need to include the source urls in your own `urls.py`. For example:

```python
from django.conf import settings
from django.contrib import admin
from django.urls import include, path

import saml2_pro_auth.urls as saml_urls

import profiles.urls
import accounts.urls

from . import views

urlpatterns = [
    path('', views.HomePage.as_view(), name='home'),
    path('about/', views.AboutPage.as_view(), name='about'),
    path('users/', include(profiles.urls, namespace='profiles')),
    path('admin/', include(admin.site.urls)),
    path('', include(accounts.urls, namespace='accounts')),
    path('', include(saml_urls, namespace='saml')),
]

```

So first import the urls via `import saml2_pro_auth.urls as saml_urls` (it's up to you if you want name it or not). Then add it to your patterns via `path('', include(saml_urls, namespace='saml'))`. This example will give you the default routes that this auth backend provides. You can also add any additional prefix to the path that you want here.

If you want to use the old function-based view URLs you can import and use those instead.

```python
import saml2_pro_auth.function_urls as saml_urls
```

**SAML_OVERRIDE_HOSTNAME (optional, default=""):** This allows you to set a specific hostname to be used in SAML requests. The default method to is detect the hostname from the `request` object. This generally works unless you are behind several layers of proxies or other caching layers. For example, running Django inside a Lambda function that is fronted by API Gateway and CloudFront could pose problems. This setting lets you set the value explicitly. The value should be a simple hostname or dotted path. Do not include a full URL, port, scheme, etc.

```python
SAML_OVERRIDE_HOSTNAME = "app.example.org"
```

**SAML_CACHE (optional, default="default"):** This lets you specify a different cache backend configuration if need you a specific type of persistent cache mechanism that differs from the `CACHES["default"]`. A persistent cache is required for only once SAML assertion processing to work. This is an important security mechanism and should not be bypassed. In local development environments, the local memory, dummy, or file caches will work fine. For stateless or multi-server high availability environments you will want to use a shared, persistent cache. Storing this in the Database is likely the easiest solution since the data is small and the number of requests should be minimal.

If your default cache is not using a shared persistent cache configuration you can add on and update this setting.

```python
SAML_CACHE = "saml2_pro_auth"

CACHES = {
    'saml2_pro_auth': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'saml2_pro_auth_cache',
    }
}

```

**SAML_REPLAY_PROTECTION (optional, default=True):** This allows you to disable the only-once assertion processing protection (SAML assertion replay protection) mechanism. It currently relies on a shared persistent caching mechanism that may not be feasible in all environments. It is strongly recommend you to keep this enabled but if there are architectural reasons or there is a low risk of replay attacks then it can still be disabled.

**SAML_REDIRECT (optional, default=None):** This tells the auth backend where to redirect users after they've logged in via the IdP. **NOTE**: This is not needed for _most_ users. Order of precedence is: SAML_REDIRECT value (if defined), RELAY_STATE provided in the SAML response, and the fallback is simply to go to the root path of your application.

**SAML_USERS_MAP (required):** This is a dict of user attribute mapping dicts. This is what makes it possible to map the attributes as they come from your IdP into attributes that are part of your User model in Django. There a few ways you can define this. The dict keys (the left-side) are the attributes as defined in YOUR User model, the dict values (the right-side) are the attributes as supplied by your IdP.

```python
## Simplest Approach, when the SAML attributes supplied by the IdP are just plain strings
## This means my User model has an 'email' and 'name' attribute while my IdP passes 'Email' and 'Username' attrs
SAML_USERS_MAP = {
    "myIdp" : {
      "email": "Email",
      "name": "Username
    }
}
```

Sometimes, IdPs might provide values as Arrays (even when it really should just be a string). This package supports that too. For example, suppose your IdP supplied user attributes with the following data structure:
`{"Email": ["foo@example.com"], "Username": "foo"}`
You simply would make the key slightly more complex where `key` is the key and `index` represents the index where the desired value is located. See below:

```python
SAML_USERS_MAP = {
    "myIdp" : {
      "email": {"key": "Email", "index": 0},
      "name": "Username
    }
```

And of course, you can use the dict structure even when there IdP supplied attribute isn't an array. For example:

```python
SAML_USERS_MAP = {
    "myIdp" : {
      "email": {"key": "Email"},
      "name": {"key": "Username"}
    }
```

**SAML_USERS_LOOKUP_ATTRIBUTE (optional, default=("username", "NameId")):**
A tuple that specifies the User model field and lookup type to be used for object lookup in the database, along with the attribute to match. It defaults to matching `username` to the `NameId` sent from the IdP. If you want to match against a different database field you would update the `key`, if you want to use a different attribute from the IdP you would update the `value`.

The attribute you match on in the Django User model should have the "unique" flag set.
(In the default User model in django only username has a unique contstraint in the DB, the same email could be used by multiple users)

This can also include Django field lookup extensions. By default the lookup will be performed as an exact match. If you
have an identity provider that sends case sensitive emails and you are storing the email in the `username` field you can still match emails in your database by using `username__iexact`. Anything before the double underscore will be used as the field name, everything after is used in the Django Query field lookup.

Defaults to `("username", "NameId")`

```python
SAML_USERS_LOOKUP_ATTRIBUTE = ("username__iexact", "NameId")
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
SAML_USERS_MAP = {
    "MyProvider" : {
      "email": dict(key="email", index=0),
      "username": dict(key="username", index=0),
      "is_superuser": dict(key="is_superuser", index=0, default=False),
      "is_staff": dict(key="is_staff", index=0, default=False)
    }
}
```

**SAML_AUTO_CREATE_USERS (optional):**
Specifies if you want users to be automatically created if they don't already exist in the database.

Defaults to True

```python
SAML_AUTO_CREATE_USERS = False
```

**SAML_PROVIDER_CONFIG_TEMPLATE** This is a base template to use for any `SamlProvider` model instances if you are using the settings model class. You can override any settings in this template to set your base configuration. This also helps you to stay DRY.

```python
PROVIDER_CONFIG_TEMPLATE = {
    "strict": True,
    "sp": {
        "x509cert": "",
        "privateKey": "",
    },
    # No one actually sets these fields in their metadata
    # "organization": {
    #     "en-US": {
    #         "name": "",
    #         "displayname": "",
    #         "url": "",
    #     }
    # },
    # "contactPerson": {
    #     "technical": {"givenName": "", "emailAddress": ""},
    #     "support": {"givenName": "", "emailAddress": ""},
    # },
    "security": {
        "nameIdEncrypted": False,
        "authnRequestsSigned": True,
        "logoutRequestSigned": True,
        "logoutResponseSigned": True,
        "signMetadata": True,
        "wantMessagesSigned": True,
        "wantAssertionsSigned": False,
        "wantAssertionsEncrypted": False,
        "wantNameId": True,
        "wantNameIdEncrypted": False,
        "wantAttributeStatement": False,
        "signatureAlgorithm": "http://www.w3.org/2000/09/xmldsig#rsa-sha256",
        "digestAlgorithm": "http://www.w3.org/2001/04/xmlenc#sha256",
    },
}
```

**SAML_PROVIDERS:** This is an extended version of the OneLogin spec [python-saml and python3-saml packages](https://github.com/onelogin/python3-saml#settings). The big difference is here you supply a dict of settings dicts where the top most key(s) must map 1:1 to the top most keys in `SAML_USERS_MAP`. Also, this package allows you to ref the cert/key files via `open()` calls. This is to allow those of you with multiple external customers to login to your platform with any N number of IdPs.

**NOTE:** Provider names (top level keys in the settings dict) must adhere to a `slug` like set of characters `[\w-]+` or `a-zA-Z0-9_-`.

Extensions to the OneLogin settings dict spec:

- The `lowercase_urlencoding` setting (default=False) can be specifed in your settings dict per provider. This allows you to support ADFS IdPs.
- The `idp_initiated_auth` setting (default=True) can be specified in your settings dict per providfer This allows you to disable IdP-initiated flows on a provider-by-provider basis. You may want to consider disable IdP-initiated flows to avoid accepting unsolicited SAML assertions and eliminate a small class of vulnerabilities and potential CSRF attacks. Setting this value to `False` will disable IdP-initiated auth.

## Class-based View Routes

| **Route**                                 | **Uses**                                                                                                                                                                                                              |
|-------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `/saml/acs/<samlp:provider>/`             | The Assertion Consumer Service Endpoint. This is where your IdP will be POSTing assertions.              |
| `/saml/sso/<samlp:provider>/`             | Use this endpoint when you want to trigger an SP-initiated login. For example, this could be the `href` of a "Login with ClientX Okta" button.                                                                      |
| `/saml/metadata/<samlp:provider>/`        | This is where the SP (ie your Django App) has metadata. Some IdPs request this to generate configuration.  |

The class-based views and routes use a custom path converter `<samlp:provider>` to create URLs from provider name strings or to automatically match a top level key of your SAML_PROVIDERS settings on requests. This also has the benefit of returning the provider settings dict and sending it to the View automatically. You must ensure that your provider names adhere to a `slug` like set of characters `[\w-]+`.

## Legacy (Function-based View) Routes

| **Route**                                 | **Uses**                                                                                                                                                                                                              |
|-------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `/sso/saml/?acs&amp;provider=MyProvider`  | The Assertion Consumer Service Endpoint. This is where your IdP will be POSTing assertions. The 'provider' query string must have a value that matches a top level key of your SAML_PROVIDERS settings.               |
| `/sso/saml/metadata?provider=MyProvider`  | This is where the SP (ie your Django App) has metadata. Some IdPs request this to generate configuration. The 'provider' query string must have a value that matches a top level key of your SAML_PROVIDERS settings. |
| `/sso/saml/?provider=MyProvider`          | Use this endpoint when you want to trigger an SP-initiated login. For example, this could be the `href`of a "Login with ClientX Okta" button.                                                                         |

## Reverse URLs

You can reference the above URLs using the standard Django `{% url ... %}` template tag or `reverse(...)` function.

```django
{% url 'saml:metadata' provider='MyProvider' %}
{% url 'saml:sso' provider='MyProvider' %}
```

Or for the function-based routes.

```django
{% url 'saml:metadata' %}?provider=MyProvider
{% url 'saml:saml2_auth' %}?acs&provider=MyProvider
```

## Gotchas

The following are things that you may run into issue with. Here are some tips.

- Ensure the value of the SP `entityId` config matches up with what you supply in your IdPs configuration.
- Your IdP may default to particular Signature type, usually `Assertion` or `Response` are the options. Depending on how you define your SAML provider config, it will dictate what this value should be.

## Wishlist and TODOs

The following are things that arent present yet but would be cool to have

- Implement logic for Single Logout Service
- Integration test with full on mock saml interactions to test the actual backend auth
- Tests add coverage to views and the authenticate() get_user() methods in the auth backend
- Models (with multi-tentant support) for idp and sp in order to facilitate management via django admin
- Add a proper CHANGELOG to release process.

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
    twine upload testpypi dist/*
    # upload to production pypi
    twine upload dist/*
    ```

1. Create a release on GitHub

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
