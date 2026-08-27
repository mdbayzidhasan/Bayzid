from django.contrib import admin

from .models import AffiliateClick, AffiliateCommission, AffiliateLink, AffiliateProfile


@admin.register(AffiliateProfile)
class AffiliateProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "code", "status", "commission_percent"]
    list_filter = ["status"]
    search_fields = ["user__email", "code"]


@admin.register(AffiliateLink)
class AffiliateLinkAdmin(admin.ModelAdmin):
    list_display = ["affiliate", "product", "created_at"]
    search_fields = ["affiliate__code", "product__name"]


@admin.register(AffiliateClick)
class AffiliateClickAdmin(admin.ModelAdmin):
    list_display = ["link", "ip_address", "created_at"]


@admin.register(AffiliateCommission)
class AffiliateCommissionAdmin(admin.ModelAdmin):
    list_display = ["affiliate", "order", "amount", "status", "created_at"]
    list_filter = ["status"]
    actions = ["approve_and_pay"]

    @admin.action(description="Approve & pay selected commissions")
    def approve_and_pay(self, request, queryset):
        from wallet.models import credit_wallet
        for commission in queryset.filter(status="pending"):
            credit_wallet(
                commission.affiliate.user, commission.amount, "commission",
                description=f"Affiliate commission for order {commission.order.order_number}",
                reference_id=str(commission.id),
            )
            commission.status = "paid"
            commission.save(update_fields=["status"])
