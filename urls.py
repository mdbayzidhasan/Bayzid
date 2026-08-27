from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import BecomeSellerView, MySellerProfileView, StoreViewSet

router = DefaultRouter()
router.register("stores", StoreViewSet, basename="store")

urlpatterns = [
    path("apply/", BecomeSellerView.as_view(), name="seller-apply"),
    path("me/", MySellerProfileView.as_view(), name="seller-me"),
] + router.urls
