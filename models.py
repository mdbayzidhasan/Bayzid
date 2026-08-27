from django.conf import settings
from django.db import models

from core.models import BaseModel


class Wallet(BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    def __str__(self):
        return f"Wallet<{self.user.email}: {self.balance}>"


class WalletTransaction(BaseModel):
    class Type(models.TextChoices):
        CREDIT = "credit", "Credit"
        DEBIT = "debit", "Debit"
        WITHDRAWAL = "withdrawal", "Withdrawal"
        REFUND = "refund", "Refund"
        COMMISSION = "commission", "Commission"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    type = models.CharField(max_length=20, choices=Type.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.COMPLETED)
    description = models.CharField(max_length=255, blank=True)
    reference_id = models.CharField(max_length=100, blank=True)  # e.g. order number, withdrawal id

    class Meta(BaseModel.Meta):
        indexes = [models.Index(fields=["wallet", "type"])]


class Withdrawal(BaseModel):
    class Method(models.TextChoices):
        BKASH = "bkash", "bKash"
        NAGAD = "nagad", "Nagad"
        BANK = "bank", "Bank Transfer"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        REJECTED = "rejected", "Rejected"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="withdrawals")
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    method = models.CharField(max_length=20, choices=Method.choices)
    account_info = models.CharField(max_length=255)  # e.g. bKash number, bank account
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    admin_note = models.CharField(max_length=255, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)


def credit_wallet(user, amount, tx_type, description="", reference_id=""):
    """Single, safe entry point for adding money to a user's wallet."""
    wallet, _ = Wallet.objects.get_or_create(user=user)
    wallet.balance = wallet.balance + amount
    wallet.save(update_fields=["balance"])
    return WalletTransaction.objects.create(
        wallet=wallet, amount=amount, type=tx_type,
        description=description, reference_id=reference_id,
    )


def debit_wallet(user, amount, tx_type, description="", reference_id=""):
    wallet, _ = Wallet.objects.get_or_create(user=user)
    if wallet.balance < amount:
        raise ValueError("Insufficient wallet balance.")
    wallet.balance = wallet.balance - amount
    wallet.save(update_fields=["balance"])
    return WalletTransaction.objects.create(
        wallet=wallet, amount=amount, type=tx_type,
        description=description, reference_id=reference_id,
    )
