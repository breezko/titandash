from django.contrib import admin
from django.contrib.admin.decorators import register

from .models.settings import ApplicationSettings

@register(ApplicationSettings)
class ApplicationSettingsAdmin(admin.ModelAdmin):
    pass
