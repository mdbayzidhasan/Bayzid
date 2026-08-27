from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CartItemViewSet, CartView, CheckoutView, OrderViewSet, WishlistViewSet

router = DefaultRouter()
router.register("cart-items", CartItemViewSet, basename="cart-item")
router.register("wishlist", WishlistViewSet, basename="wishlist")
router.register("", OrderViewSet, basename="order")

urlpatterns = [
    path("cart/", CartView.as_view(), name="cart"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
] + router.urls
