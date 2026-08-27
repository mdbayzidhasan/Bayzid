from rest_framework import serializers

from .models import AffiliateClick, AffiliateCommission, AffiliateLink, AffiliateProfile


class AffiliateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AffiliateProfile
        fields = ["id", "code", "status", "commission_percent"]
        read_only_fields = fields


class AffiliateLinkSerializer(serializers.ModelSerializer):
    path = serializers.CharField(read_only=True)

    class Meta:
        model = AffiliateLink
        fields = ["id", "product", "path", "created_at"]
        read_only_fields = ["id", "path", "created_at"]


class AffiliateCommissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AffiliateCommission
        fields = ["id", "order", "amount", "status", "created_at"]
        read_only_fields = fields
