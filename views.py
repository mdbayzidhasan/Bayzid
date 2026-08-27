from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import SellerProfile, Store
from .serializers import SellerApplicationSerializer, SellerProfileSerializer, StoreSerializer


class BecomeSellerView(generics.CreateAPIView):
    """Buyer applies to become a seller. Status starts as 'pending' for admin approval."""
    serializer_class = SellerApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MySellerProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.seller_profile
        except SellerProfile.DoesNotExist:
            return Response({"detail": "Not a seller yet."}, status=404)
        return Response(SellerProfileSerializer(profile).data)


class StoreViewSet(viewsets.ModelViewSet):
    """Sellers manage their own store; public can read active stores."""
    queryset = Store.objects.filter(is_active=True)
    serializer_class = StoreSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if self.action in ["list", "retrieve"]:
            return Store.objects.filter(is_active=True)
        return Store.objects.filter(seller__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user.seller_profile)
