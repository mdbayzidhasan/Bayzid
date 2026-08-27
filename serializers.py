from rest_framework import serializers

from orders.models import OrderItem
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Review
        fields = ["id", "product", "user_name", "order_item", "rating", "comment", "image", "created_at"]
        read_only_fields = ["id", "user_name", "created_at"]

    def validate_order_item(self, order_item):
        request = self.context["request"]
        if order_item.order.buyer != request.user:
            raise serializers.ValidationError("You can only review items you purchased.")
        if order_item.status != OrderItem._meta.get_field("status").default and order_item.status != "delivered":
            raise serializers.ValidationError("You can review a product only after it has been delivered.")
        return order_item

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        validated_data["product"] = validated_data["order_item"].product
        return super().create(validated_data)
