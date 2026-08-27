from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Wallet, WalletTransaction, Withdrawal, debit_wallet
from .serializers import WalletSerializer, WalletTransactionSerializer, WithdrawalSerializer


class MyWalletView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        return Response(WalletSerializer(wallet).data)


class WalletTransactionListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        qs = wallet.transactions.all()[:100]
        return Response(WalletTransactionSerializer(qs, many=True).data)


class WithdrawalViewSet(viewsets.ModelViewSet):
    serializer_class = WithdrawalSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "head"]

    def get_queryset(self):
        return Withdrawal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Reserve funds immediately by debiting the wallet; admin approval
        # later moves status forward (approve/reject handled in admin/API).
        withdrawal = serializer.save(user=self.request.user)
        debit_wallet(
            self.request.user, withdrawal.amount, "withdrawal",
            description="Withdrawal request", reference_id=str(withdrawal.id),
        )
