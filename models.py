from django.conf import settings
from django.db import models

from core.models import BaseModel
from orders.models import OrderItem
from products.models import Product


class Review(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    order_item = models.ForeignKey(
        OrderItem, on_delete=models.CASCADE, related_name="review",
        help_text="Proof of purchase — required so only verified buyers can review.",
    )
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    image = models.ImageField(upload_to="reviews/", null=True, blank=True)
    is_verified_purchase = models.BooleanField(default=True)

    class Meta(BaseModel.Meta):
        unique_together = [["user", "order_item"]]
        indexes = [models.Index(fields=["product"])]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._recalculate_product_rating()

    def _recalculate_product_rating(self):
        from django.db.models import Avg, Count
        agg = Review.objects.filter(product=self.product).aggregate(avg=Avg("rating"), total=Count("id"))
        Product.objects.filter(pk=self.product_id).update(
            average_rating=round(agg["avg"] or 0, 2), review_count=agg["total"]
        )
