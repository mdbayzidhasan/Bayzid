from django.db.models import Count, Sum
from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AffiliateClick, AffiliateCommission, AffiliateLink, AffiliateProfile
from .serializers import AffiliateCommissionSerializer, AffiliateLinkSerializer, AffiliateProfileSerializer


class BecomeAffiliateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        profile, created = AffiliateProfile.objects.get_or_create(user=request.user)
        return Response(AffiliateProfileSerializer(profile).data, status=201 if created else 200)


class MyAffiliateDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.affiliate_profile
        except AffiliateProfile.DoesNotExist:
            return Response({"detail": "Not an affiliate yet."}, status=404)

        total_clicks = AffiliateClick.objects.filter(link__affiliate=profile).count()
        commissions = AffiliateCommission.objects.filter(affiliate=profile)
        total_orders = commissions.values("order").distinct().count()
        totals = commissions.aggregate(
            total_commission=Sum("amount"),
            pending=Sum("amount", filter=models_Q_pending()),
        )
        conversion_rate = (total_orders / total_clicks * 100) if total_clicks else 0

        return Response({
            "profile": AffiliateProfileSerializer(profile).data,
            "total_clicks": total_clicks,
            "total_orders": total_orders,
            "conversion_rate": round(conversion_rate, 2),
            "total_commission": totals["total_commission"] or 0,
            "pending_commission": totals["pending"] or 0,
            "available_balance": request.user.wallet.balance if hasattr(request.user, "wallet") else 0,
        })


def models_Q_pending():
    from django.db.models import Q
    return Q(status=AffiliateCommission.Status.PENDING)


class AffiliateLinkViewSet(viewsets.ModelViewSet):
    serializer_class = AffiliateLinkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AffiliateLink.objects.filter(affiliate=self.request.user.affiliate_profile)

    def perform_create(self, serializer):
        serializer.save(affiliate=self.request.user.affiliate_profile)


class TrackClickView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, pk):
        try:
            link = AffiliateLink.objects.get(pk=pk)
        except AffiliateLink.DoesNotExist:
            return Response({"detail": "Not found."}, status=404)
        AffiliateClick.objects.create(
            link=link,
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:255],
        )
        return Response({"detail": "Click recorded."})
