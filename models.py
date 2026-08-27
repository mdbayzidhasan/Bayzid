import uuid

from django.db import models


class BaseModel(models.Model):
    """
    Abstract base for all Bayzid models.
    Provides a UUID primary key (safe to expose in URLs/APIs) plus
    created/updated timestamps.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


def generate_order_number():
    """Human-friendly, sortable order number: BYZ-YYYYMMDD-XXXXXX"""
    import random
    from django.utils import timezone

    date_part = timezone.now().strftime("%Y%m%d")
    rand_part = "".join(random.choices("0123456789", k=6))
    return f"BYZ-{date_part}-{rand_part}"
