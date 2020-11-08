from django.contrib import admin
from django.urls import include, path

import saml2_pro_auth.function_urls as legacy_saml_urls
import saml2_pro_auth.urls as saml_urls

from .views import IndexView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", IndexView.as_view(), name="index"),
    path("", include((saml_urls), namespace="saml")),
    path("func/", include((legacy_saml_urls), namespace="saml_func")),
]
