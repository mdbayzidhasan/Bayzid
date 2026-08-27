from rest_framework import serializers

from .models import Category, Product, ProductImage, ProductVariant


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "parent", "image", "description", "is_active", "children"]

    def get_children(self, obj):
        return CategorySerializer(obj.children.filter(is_active=True), many=True).data


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "alt_text", "is_primary", "sort_order"]


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ["id", "name", "sku_suffix", "price_delta", "stock_quantity"]


class ProductListSerializer(serializers.ModelSerializer):
    primary_image = serializers.SerializerMethodField()
    seller_name = serializers.CharField(source="seller.name", read_only=True)
    final_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "price", "discount_percent", "final_price",
            "average_rating", "review_count", "seller_name", "primary_image",
            "status", "stock_quantity",
        ]

    def get_primary_image(self, obj):
        img = obj.images.filter(is_primary=True).first() or obj.images.first()
        return img.image.url if img else None


class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    seller_name = serializers.CharField(source="seller.name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    final_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "sku", "description", "specifications",
            "price", "discount_percent", "final_price", "stock_quantity",
            "status", "average_rating", "review_count", "seller_name",
            "category", "category_name", "images", "variants", "created_at",
        ]


class ProductWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "name", "slug", "sku", "category", "description", "specifications",
            "price", "discount_percent", "stock_quantity", "weight_kg",
            "is_affiliate_enabled",
        ]

    def create(self, validated_data):
        validated_data["seller"] = self.context["request"].user.seller_profile.store
        validated_data["status"] = Product.Status.PENDING
        return super().create(validated_data)
