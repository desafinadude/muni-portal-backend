from django.contrib import admin
from muni_portal.core.models import Webhook, Webpush


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    list_display = ("id", "data", "created_at")
    list_filter = ("created_at",)


@admin.register(Webpush)
class WebhookAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "endpoint", "created_at")
    list_filter = ("created_at",)
    raw_id_fields = ("user",)
