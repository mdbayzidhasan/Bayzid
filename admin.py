from django.contrib import admin

from .models import Wallet, WalletTransaction, Withdrawal


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ["user", "balance", "updated_at"]
    search_fields = ["user__email"]


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ["wallet", "amount", "type", "status", "created_at"]
    list_filter = ["type", "status"]
    readonly_fields = ["id", "created_at"]


@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ["user", "amount", "method", "status", "created_at", "processed_at"]
    list_filter = ["status", "method"]
    search_fields = ["user__email"]
    actions = ["mark_completed", "mark_rejected"]

    @admin.action(description="Mark selected withdrawals as completed")
    def mark_completed(self, request, queryset):
        from django.utils import timezone
        queryset.update(status="completed", processed_at=timezone.now())

    @admin.action(description="Mark selected withdrawals as rejected (refunds wallet)")
    def mark_rejected(self, request, queryset):
        from django.utils import timezone
        from .models import credit_wallet
        for w in queryset.filter(status="pending"):
            credit_wallet(w.user, w.amount, "refund", description="Withdrawal rejected", reference_id=str(w.id))
            w.status = "rejected"
            w.processed_at = timezone.now()
            w.save(update_fields=["status", "processed_at"])
