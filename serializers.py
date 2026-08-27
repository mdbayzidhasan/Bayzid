from django.contrib.auth import password_validation
from django.contrib.auth.hashers import check_password, make_password
from rest_framework import serializers

from .models import Address, OTP, Profile, User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "phone_number",
            "password", "confirm_password", "account_type",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("confirm_password"):
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        password_validation.validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.password = make_password(password)
        user.is_active = True
        user.save()
        Profile.objects.create(user=user)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "username", "email", "phone_number", "account_type",
            "is_email_verified", "is_phone_verified", "date_joined",
        ]
        read_only_fields = fields


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ["user", "avatar", "date_of_birth", "gender", "bio"]


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"
        read_only_fields = ["id", "user", "created_at"]


class OTPRequestSerializer(serializers.Serializer):
    identifier = serializers.CharField(help_text="Email or phone number")
    purpose = serializers.ChoiceField(choices=OTP.Purpose.choices)


class OTPVerifySerializer(serializers.Serializer):
    identifier = serializers.CharField()
    purpose = serializers.ChoiceField(choices=OTP.Purpose.choices)
    code = serializers.CharField(max_length=6, min_length=6)


class PasswordResetConfirmSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    code = serializers.CharField(max_length=6, min_length=6)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        password_validation.validate_password(attrs["new_password"])
        return attrs
