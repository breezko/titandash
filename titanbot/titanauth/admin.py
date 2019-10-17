from django.contrib import admin
from django.contrib.admin.decorators import register

from titanauth.models.release_info import ReleaseInfo


@register(ReleaseInfo)
class ReleaseInfoAdmin(admin.ModelAdmin):
    list_display = ["version", "grabbed"]
