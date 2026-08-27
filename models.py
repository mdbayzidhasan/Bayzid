from django.db import models

from core.models import BaseModel
from sellers.models import Store


class Category(BaseModel):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    image = models.ImageField(upload_to="categories/", null=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta(BaseModel.Meta):
        verbose_name_plural = "categories"
        indexes = [models.Index(fields=["slug"]), models.Index(fields=["parent"])]

    def __str__(self):
        return self.name


class Product(BaseModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING = "pending", "Pending Approval"
        PUBLISHED = "published", "Published"
        REJECTED = "rejected", "Rejected"
        OUT_OF_STOCK = "out_of_stock", "Out of Stock"

    seller = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=250)
    slug = models.SlugField(max_length=270, unique=True)
    sku = models.CharField(max_length=64, unique=True)
    description = models.TextField()
    specifications = models.JSONField(default=dict, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    stock_quantity = models.PositiveIntegerField(default=0)
    weight_kg = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    is_affiliate_enabled = models.BooleanField(default=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    review_count = models.PositiveIntegerField(default=0)

    class Meta(BaseModel.Meta):
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["status"]),
            models.Index(fields=["category"]),
            models.Index(fields=["seller"]),
        ]

    @property
    def final_price(self):
        if self.discount_percent:
            return round(self.price * (1 - self.discount_percent / 100), 2)
        return self.price

    @property
    def in_stock(self):
        return self.stock_quantity > 0

    def __str__(self):
        return self.name


class ProductImage(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/")
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta(BaseModel.Meta):
        ordering = ["sort_order", "-created_at"]


class ProductVariant(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    name = models.CharField(max_length=100)  # e.g. "Color: Red / Size: L"
    sku_suffix = models.CharField(max_length=32, blank=True)
    price_delta = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} — {self.name}"
