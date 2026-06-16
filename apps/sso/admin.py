from django.contrib import admin

from apps.sso.models import ExternalAppWorkspace


@admin.register(ExternalAppWorkspace)
class ExternalAppWorkspaceAdmin(admin.ModelAdmin):
    list_display = ("external_app_slug", "external_app_id", "workspace", "organization", "created_at")
    search_fields = ("external_app_id", "external_app_slug")
    readonly_fields = ("created_at", "updated_at")
