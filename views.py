from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.permissions import IsProductOwnerSeller
from .models import Category, Product, ProductImage, ProductVariant
from .serializers import (
    CategorySerializer, ProductDetailSerializer, ProductImageSerializer,
    ProductListSerializer, ProductVariantSerializer, ProductWriteSerializer,
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_active=True, parent__isnull=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"


class ProductViewSet(viewsets.ModelViewSet):
    """
    Public: list/retrieve published products only.
    Sellers: full CRUD scoped to their own store's products.
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsProductOwnerSeller]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "seller", "status"]
    search_fields = ["name", "description", "sku"]
    ordering_fields = ["price", "average_rating", "created_at"]
    lookup_field = "slug"

    def get_queryset(self):
        if self.action in ["list", "retrieve"] and not self._is_owner_request():
            return Product.objects.filter(status=Product.Status.PUBLISHED)
        if self.request.user.is_authenticated and hasattr(self.request.user, "seller_profile"):
            return Product.objects.filter(seller__seller=self.request.user.seller_profile)
        return Product.objects.filter(status=Product.Status.PUBLISHED)

    def _is_owner_request(self):
        return self.request.query_params.get("mine") == "true"

    def get_serializer_class(self):
        if self.action == "list":
            return ProductListSerializer
        if self.action in ["create", "update", "partial_update"]:
            return ProductWriteSerializer
        return ProductDetailSerializer

    @action(detail=True, methods=["post"], parser_classes=[])
    def upload_image(self, request, slug=None):
        product = self.get_object()
        serializer = ProductImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product)
        return Response(serializer.data, status=201)

    @action(detail=True, methods=["post"])
    def add_variant(self, request, slug=None):
        product = self.get_object()
        serializer = ProductVariantSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product)
        return Response(serializer.data, status=201)
