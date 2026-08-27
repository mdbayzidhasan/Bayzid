from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Address, OTP, Profile, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["email", "username", "phone_number", "account_type", "is_email_verified", "is_active", "date_joined"]
    list_filter = ["account_type", "is_active", "is_email_verified", "is_phone_verified"]
    search_fields = ["email", "username", "phone_number"]
    ordering = ["-date_joined"]
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Bayzid", {"fields": ("account_type", "phone_number", "is_email_verified", "is_phone_verified")}),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "gender", "date_of_birth"]
    search_fields = ["user__email"]


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ["user", "label", "city", "is_default"]
    list_filter = ["city", "is_default"]
    search_fields = ["user__email", "recipient_name"]


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ["user", "purpose", "channel", "is_used", "created_at", "expires_at"]
    list_filter = ["purpose", "channel", "is_used"]
    readonly_fields = ["code", "created_at"]
    search_fields = ["user__email"]
