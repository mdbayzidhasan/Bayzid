from django.utils import timezone
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Payment
from .serializers import PaymentSerializer


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only from the client's perspective. Actual gateway callbacks
    (bKash/Nagad/card webhooks) should hit a dedicated, signature-verified
    webhook endpoint — not this viewset — wired up per-provider using the
    credentials in settings (never hard-coded).
    """
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(order__buyer=self.request.user)


class MarkCODDeliveredView(viewsets.ViewSet):
    """Seller/admin confirms a Cash on Delivery payment was collected."""
    permission_classes = [permissions.IsAdminUser]

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        payment = Payment.objects.get(pk=pk, method=Payment.Method.COD)
        payment.status = Payment.Status.PAID
        payment.paid_at = timezone.now()
        payment.save(update_fields=["status", "paid_at"])
        return Response(PaymentSerializer(payment).data)
