from rest_framework import serializers

from products.serializers import ProductListSerializer
from .models import Cart, CartItem, Coupon, Order, OrderItem, Wishlist


class CartItemSerializer(serializers.ModelSerializer):
    product_detail = ProductListSerializer(source="product", read_only=True)
    line_total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_detail", "quantity", "saved_for_later", "line_total"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "items", "subtotal"]


class WishlistSerializer(serializers.ModelSerializer):
    product_detail = ProductListSerializer(source="product", read_only=True)

    class Meta:
        model = Wishlist
        fields = ["id", "product", "product_detail", "created_at"]


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "seller_store", "quantity", "unit_price", "line_total", "status"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "order_number", "shipping_address", "coupon", "affiliate_code",
            "subtotal", "discount_total", "delivery_charge", "grand_total",
            "status", "items", "created_at",
        ]
        read_only_fields = [
            "id", "order_number", "subtotal", "discount_total",
            "delivery_charge", "grand_total", "status", "items", "created_at",
        ]


class CheckoutSerializer(serializers.Serializer):
    shipping_address = serializers.UUIDField()
    coupon_code = serializers.CharField(required=False, allow_blank=True)
    affiliate_code = serializers.CharField(required=False, allow_blank=True)
    payment_method = serializers.ChoiceField(choices=["bkash", "nagad", "card", "cod"])
