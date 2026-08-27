from rest_framework.routers import DefaultRouter

from .views import BannerViewSet, NotificationViewSet

router = DefaultRouter()
router.register("banners", BannerViewSet, basename="banner")
router.register("", NotificationViewSet, basename="notification")

urlpatterns = router.urls
