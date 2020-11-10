from django.contrib import admin

from .models import SamlProvider


@admin.register(SamlProvider)
class SamlProviderAdmin(admin.ModelAdmin):
    readonly_fields = ("id",)
