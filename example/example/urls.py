from django.contrib import admin
from django.urls import include, path

import saml2_pro_auth.urls as saml_urls

from .views import IndexView, logout

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", IndexView.as_view(), name="index"),
    path("logout/", logout, name="logout"),
    path("", include((saml_urls), namespace="saml")),
]
