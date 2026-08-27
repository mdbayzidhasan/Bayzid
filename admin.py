from django.contrib import admin

from .models import SellerProfile, Store


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ["business_name", "user", "status", "commission_rate_percent", "created_at"]
    list_filter = ["status"]
    search_fields = ["business_name", "user__email"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ["name", "seller", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
