from django.conf import settings
from django.db import models

from core.models import BaseModel


class SellerProfile(BaseModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        SUSPENDED = "suspended", "Suspended"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="seller_profile"
    )
    business_name = models.CharField(max_length=200)
    business_registration_no = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    commission_rate_percent = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)

    @property
    def is_approved(self):
        return self.status == self.Status.APPROVED

    def __str__(self):
        return self.business_name


class Store(BaseModel):
    seller = models.OneToOneField(SellerProfile, on_delete=models.CASCADE, related_name="store")
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    logo = models.ImageField(upload_to="stores/logos/", null=True, blank=True)
    banner = models.ImageField(upload_to="stores/banners/", null=True, blank=True)
    description = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta(BaseModel.Meta):
        indexes = [models.Index(fields=["slug"])]

    def __str__(self):
        return self.name
