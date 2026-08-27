import random
import string

from django.conf import settings
from django.db import models

from core.models import BaseModel
from products.models import Product


def generate_affiliate_code():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=8))


class AffiliateProfile(BaseModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        SUSPENDED = "suspended", "Suspended"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="affiliate_profile")
    code = models.CharField(max_length=20, unique=True, default=generate_affiliate_code)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.APPROVED)
    commission_percent = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)

    def __str__(self):
        return f"{self.user.email} ({self.code})"


class AffiliateLink(BaseModel):
    affiliate = models.ForeignKey(AffiliateProfile, on_delete=models.CASCADE, related_name="links")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="affiliate_links")

    class Meta(BaseModel.Meta):
        unique_together = [["affiliate", "product"]]

    @property
    def path(self):
        return f"/product/{self.product.slug}/?ref={self.affiliate.code}"


class AffiliateClick(BaseModel):
    link = models.ForeignKey(AffiliateLink, on_delete=models.CASCADE, related_name="clicks")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)

    class Meta(BaseModel.Meta):
        indexes = [models.Index(fields=["link"])]


class AffiliateCommission(BaseModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        PAID = "paid", "Paid"
        REVERSED = "reversed", "Reversed"

    affiliate = models.ForeignKey(AffiliateProfile, on_delete=models.CASCADE, related_name="commissions")
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="affiliate_commissions")
    order_item = models.ForeignKey("orders.OrderItem", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    class Meta(BaseModel.Meta):
        indexes = [models.Index(fields=["affiliate", "status"])]


def record_commission_for_order_item(order_item, affiliate_code):
    """
    Backend-only, authoritative commission calculation. Never trust a
    commission amount sent from the frontend — always derive it here from
    the affiliate's configured commission_percent and the order item total.
    """
    try:
        affiliate = AffiliateProfile.objects.get(code=affiliate_code, status=AffiliateProfile.Status.APPROVED)
    except AffiliateProfile.DoesNotExist:
        return None

    if not order_item.product.is_affiliate_enabled:
        return None

    amount = round(order_item.line_total * (affiliate.commission_percent / 100), 2)
    return AffiliateCommission.objects.create(
        affiliate=affiliate,
        order=order_item.order,
        order_item=order_item,
        amount=amount,
    )
