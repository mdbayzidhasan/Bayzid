"""
Delivery layer for OTP codes. Kept separate from views/models so real
provider credentials only ever live in environment variables and are
touched in exactly one place.
"""
from django.conf import settings
from django.core.mail import send_mail


def send_otp_email(user, otp):
    send_mail(
        subject="Your Bayzid verification code",
        message=(
            f"Hi {user.username},\n\n"
            f"Your Bayzid verification code is {otp.code}. "
            f"It expires in {settings.OTP_EXPIRY_MINUTES} minutes.\n\n"
            "If you did not request this, you can ignore this email."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


def send_otp_sms(user, otp):
    """
    Placeholder SMS architecture. Wire up a real provider (e.g. an SMS
    aggregator common in Bangladesh) here using settings.SMS_GATEWAY_API_KEY.
    Never hard-code credentials — read them from environment variables only.
    """
    if not settings.SMS_GATEWAY_API_KEY:
        # No provider configured — no-op in development.
        return
    # Example shape only:
    # requests.post(SMS_PROVIDER_URL, json={
    #     "api_key": settings.SMS_GATEWAY_API_KEY,
    #     "sender_id": settings.SMS_GATEWAY_SENDER_ID,
    #     "to": user.phone_number,
    #     "message": f"Your Bayzid code is {otp.code}",
    # })


def dispatch_otp(user, otp):
    if otp.channel == otp.Channel.SMS and user.phone_number:
        send_otp_sms(user, otp)
    else:
        send_otp_email(user, otp)
