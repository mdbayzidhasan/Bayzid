from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "order", "method", "amount", "status", "gateway_reference", "paid_at", "created_at"]
        read_only_fields = fields
