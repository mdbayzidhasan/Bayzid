from decimal import Decimal

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Address
from products.models import Product
from .models import Cart, CartItem, Coupon, Order, OrderItem, Wishlist
from .serializers import (
    CartItemSerializer, CartSerializer, CheckoutSerializer, OrderSerializer,
    WishlistSerializer,
)

DELIVERY_CHARGE = Decimal("60.00")


class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return Response(CartSerializer(cart).data)


class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart.items.all()

    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        product = serializer.validated_data["product"]
        existing = cart.items.filter(product=product).first()
        if existing:
            existing.quantity += serializer.validated_data.get("quantity", 1)
            existing.save(update_fields=["quantity"])
        else:
            serializer.save(cart=cart)


class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "delete", "head"]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(buyer=self.request.user)


class CheckoutView(APIView):
    """
    Creates the order from the buyer's current cart. Stock, pricing, coupon
    validity, and affiliate commission are all recalculated server-side —
    nothing about price or commission is trusted from the request body.
    """
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        cart = get_object_or_404(Cart, user=request.user)
        items = list(cart.items.filter(saved_for_later=False).select_related("product"))
        if not items:
            return Response({"detail": "Your cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        address = get_object_or_404(Address, id=data["shipping_address"], user=request.user)

        subtotal = sum((item.line_total for item in items), Decimal("0"))
        discount_total = Decimal("0")
        coupon = None
        coupon_code = data.get("coupon_code")
        if coupon_code:
            coupon = Coupon.objects.filter(
                code=coupon_code, is_active=True,
                valid_from__lte=timezone.now(), valid_until__gte=timezone.now(),
            ).first()
            if coupon:
                if coupon.discount_type == Coupon.DiscountType.PERCENT:
                    discount_total = round(subtotal * coupon.discount_value / 100, 2)
                else:
                    discount_total = min(coupon.discount_value, subtotal)

        grand_total = subtotal - discount_total + DELIVERY_CHARGE

        for item in items:
            if item.quantity > item.product.stock_quantity:
                return Response(
                    {"detail": f"Insufficient stock for {item.product.name}."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        order = Order.objects.create(
            buyer=request.user,
            shipping_address=address,
            coupon=coupon,
            affiliate_code=data.get("affiliate_code", ""),
            subtotal=subtotal,
            discount_total=discount_total,
            delivery_charge=DELIVERY_CHARGE,
            grand_total=grand_total,
        )

        order_items = []
        for item in items:
            product = item.product
            product.stock_quantity -= item.quantity
            if product.stock_quantity == 0:
                product.status = Product.Status.OUT_OF_STOCK
            product.save(update_fields=["stock_quantity", "status"])

            order_item = OrderItem.objects.create(
                order=order,
                product=product,
                seller_store=product.seller,
                quantity=item.quantity,
                unit_price=product.final_price,
                line_total=item.line_total,
            )
            order_items.append(order_item)

        if coupon:
            coupon.times_used += 1
            coupon.save(update_fields=["times_used"])

        # Affiliate commission — computed server-side only.
        if data.get("affiliate_code"):
            from affiliates.models import record_commission_for_order_item
            for order_item in order_items:
                record_commission_for_order_item(order_item, data["affiliate_code"])

        # Create the (pending) payment record; gateway handling lives in `payments`.
        from payments.models import Payment
        Payment.objects.create(
            order=order,
            method=data["payment_method"],
            amount=grand_total,
            status=Payment.Status.PENDING if data["payment_method"] != "cod" else Payment.Status.PENDING,
        )

        cart.items.filter(saved_for_later=False).delete()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
