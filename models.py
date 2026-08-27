from django.conf import settings
from django.db import models

from core.models import BaseModel


class Notification(BaseModel):
    class Type(models.TextChoices):
        ORDER_PLACED = "order_placed", "Order Placed"
        ORDER_SHIPPED = "order_shipped", "Order Shipped"
        ORDER_DELIVERED = "order_delivered", "Order Delivered"
        SELLER_APPROVED = "seller_approved", "Seller Approved"
        PRODUCT_APPROVED = "product_approved", "Product Approved"
        WITHDRAWAL_UPDATE = "withdrawal_update", "Withdrawal Update"
        AFFILIATE_COMMISSION = "affiliate_commission", "Affiliate Commission"
        PASSWORD_CHANGED = "password_changed", "Password Changed"
        OTP = "otp", "OTP"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    type = models.CharField(max_length=30, choices=Type.choices)
    title = models.CharField(max_length=200)
    message = models.CharField(max_length=500)
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=255, blank=True)

    class Meta(BaseModel.Meta):
        indexes = [models.Index(fields=["user", "is_read"])]


class Banner(BaseModel):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to="banners/")
    link_url = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta(BaseModel.Meta):
        ordering = ["sort_order", "-created_at"]


def notify(user, type_, title, message, link=""):
    return Notification.objects.create(user=user, type=type_, title=title, message=message, link=link)
