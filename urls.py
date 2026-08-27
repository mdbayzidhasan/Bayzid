from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import MyWalletView, WalletTransactionListView, WithdrawalViewSet

router = DefaultRouter()
router.register("withdrawals", WithdrawalViewSet, basename="withdrawal")

urlpatterns = [
    path("me/", MyWalletView.as_view(), name="wallet-me"),
    path("transactions/", WalletTransactionListView.as_view(), name="wallet-transactions"),
] + router.urls
