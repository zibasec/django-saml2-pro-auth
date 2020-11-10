from django.urls import include, path

import saml2_pro_auth.urls as saml_urls

urlpatterns = [
    path("", include((saml_urls))),
]
