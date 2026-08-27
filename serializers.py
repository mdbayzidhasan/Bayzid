from rest_framework import serializers

from .models import SellerProfile, Store


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ["id", "name", "slug", "logo", "banner", "description", "contact_email", "contact_phone", "is_active"]
        read_only_fields = ["id"]


class SellerProfileSerializer(serializers.ModelSerializer):
    store = StoreSerializer(read_only=True)

    class Meta:
        model = SellerProfile
        fields = ["id", "business_name", "business_registration_no", "status", "commission_rate_percent", "store"]
        read_only_fields = ["id", "status", "commission_rate_percent"]


class SellerApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerProfile
        fields = ["business_name", "business_registration_no"]
