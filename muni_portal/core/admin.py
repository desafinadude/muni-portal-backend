from django.contrib import admin
from muni_portal.core.models import Webhook, WebPushSubscription, WebPushNotification, WebPushNotificationResult


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    list_display = ("id", "data", "created_at")
    list_filter = ("created_at",)


@admin.register(WebPushSubscription)
class WebpushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at")
    list_filter = ("created_at",)
    raw_id_fields = ("user",)


@admin.register(WebPushNotification)
class WebPushNotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "created_at")
    list_filter = ("created_at",)
    readonly_fields = ("status",)

    def save_model(self, request, obj, form, change):
        super(WebPushNotificationAdmin, self).save_model(request, obj, form, change)
        send_webpush_notification(obj)


@admin.register(WebPushNotificationResult)
class WebPushNotificationResultAdmin(admin.ModelAdmin):
    list_display = ("id", "notification", "subscription", "status_code", "created_at")
    list_filter = ("created_at",)
    raw_id_fields = ("notification", "subscription",)
