from django.contrib import admin

from .models import Banner, Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["user", "type", "title", "is_read", "created_at"]
    list_filter = ["type", "is_read"]
    search_fields = ["user__email", "title"]


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ["title", "is_active", "sort_order"]
    list_filter = ["is_active"]
