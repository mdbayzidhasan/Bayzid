from django.db.models import Q
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Address, OTP, Profile, User
from .serializers import (
    AddressSerializer, OTPRequestSerializer, OTPVerifySerializer,
    PasswordResetConfirmSerializer, ProfileSerializer, RegisterSerializer,
    UserSerializer,
)
from .services import dispatch_otp


def find_user_by_identifier(identifier):
    return User.objects.filter(
        Q(email__iexact=identifier) | Q(phone_number=identifier)
    ).first()


class EmailOrPhoneTokenObtainSerializer(TokenObtainPairSerializer):
    """Allows login with either email or phone number in the 'username' field."""

    def validate(self, attrs):
        identifier = attrs.get(self.username_field)
        user = find_user_by_identifier(identifier)
        if user is not None:
            attrs[self.username_field] = user.email
        return super().validate(attrs)


class LoginView(TokenObtainPairView):
    serializer_class = EmailOrPhoneTokenObtainSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        otp = OTP.generate(user, OTP.Purpose.REGISTRATION, channel=OTP.Channel.EMAIL)
        dispatch_otp(user, otp)

        return Response(
            {"detail": "Account created. Check your email for a verification code.",
             "user": UserSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )


class RequestOTPView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = "otp"

    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        identifier = serializer.validated_data["identifier"]
        purpose = serializer.validated_data["purpose"]

        user = find_user_by_identifier(identifier)
        if user is None:
            # Do not reveal whether an account exists.
            return Response({"detail": "If an account exists, a code has been sent."})

        otp = OTP.generate(user, purpose)
        dispatch_otp(user, otp)
        return Response({"detail": "If an account exists, a code has been sent."})


class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = find_user_by_identifier(data["identifier"])
        if user is None:
            return Response({"detail": "Invalid code."}, status=status.HTTP_400_BAD_REQUEST)

        otp = (
            OTP.objects.filter(user=user, purpose=data["purpose"], is_used=False)
            .order_by("-created_at")
            .first()
        )
        if otp is None or not otp.is_valid():
            return Response({"detail": "Code expired or invalid."}, status=status.HTTP_400_BAD_REQUEST)

        if otp.code != data["code"]:
            otp.attempts += 1
            otp.save(update_fields=["attempts"])
            return Response({"detail": "Incorrect code."}, status=status.HTTP_400_BAD_REQUEST)

        otp.is_used = True
        otp.save(update_fields=["is_used"])

        if data["purpose"] == OTP.Purpose.REGISTRATION:
            if otp.channel == OTP.Channel.SMS:
                user.is_phone_verified = True
            else:
                user.is_email_verified = True
            user.save(update_fields=["is_email_verified", "is_phone_verified"])

        return Response({"detail": "Verified successfully."})


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = find_user_by_identifier(data["identifier"])
        if user is None:
            return Response({"detail": "Invalid code."}, status=status.HTTP_400_BAD_REQUEST)

        otp = (
            OTP.objects.filter(
                user=user, purpose=OTP.Purpose.PASSWORD_RESET, is_used=False
            )
            .order_by("-created_at")
            .first()
        )
        if otp is None or not otp.is_valid() or otp.code != data["code"]:
            return Response({"detail": "Code expired or invalid."}, status=status.HTTP_400_BAD_REQUEST)

        user.password = make_password(data["new_password"])
        user.save(update_fields=["password"])
        otp.is_used = True
        otp.save(update_fields=["is_used"])

        return Response({"detail": "Password successfully changed."})


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        return Response(ProfileSerializer(profile).data)

    def patch(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
