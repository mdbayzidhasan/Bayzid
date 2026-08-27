from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    AffiliateLinkViewSet, BecomeAffiliateView, MyAffiliateDashboardView, TrackClickView,
)

router = DefaultRouter()
router.register("links", AffiliateLinkViewSet, basename="affiliate-link")

urlpatterns = [
    path("apply/", BecomeAffiliateView.as_view(), name="affiliate-apply"),
    path("dashboard/", MyAffiliateDashboardView.as_view(), name="affiliate-dashboard"),
    path("links/<uuid:pk>/track-click/", TrackClickView.as_view(), name="affiliate-track-click"),
] + router.urls
