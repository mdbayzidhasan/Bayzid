from rest_framework import serializers

from .models import Wallet, WalletTransaction, Withdrawal


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ["id", "balance"]


class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = ["id", "amount", "type", "status", "description", "reference_id", "created_at"]


class WithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdrawal
        fields = ["id", "amount", "method", "account_info", "status", "created_at"]
        read_only_fields = ["id", "status", "created_at"]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value
