from django.conf import settings
from django.core.mail import send_mail


def send_otp_email(user, otp_code):
    """Send the OTP code to the user's email address.

    Uses Django's console email backend by default in local development,
    so the OTP will simply be printed to the terminal running `runserver`.
    Configure real SMTP settings in .env to send actual emails.
    """
    subject = 'Your verification code'
    message = (
        f'Hi {user.name},\n\n'
        f'Your One-Time Password (OTP) is: {otp_code}\n'
        f'This code will expire in {settings.OTP_EXPIRY_MINUTES} minutes.\n\n'
        f'If you did not request this, please ignore this email.'
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


def set_auth_cookies(response, access_token, refresh_token):
    """Attach access/refresh JWTs to the response as HTTP-only cookies."""
    response.set_cookie(
        key=settings.AUTH_COOKIE_ACCESS,
        value=str(access_token),
        httponly=settings.AUTH_COOKIE_HTTPONLY,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        path=settings.AUTH_COOKIE_PATH,
    )
    response.set_cookie(
        key=settings.AUTH_COOKIE_REFRESH,
        value=str(refresh_token),
        httponly=settings.AUTH_COOKIE_HTTPONLY,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        path=settings.AUTH_COOKIE_PATH,
    )
    return response


def clear_auth_cookies(response):
    response.delete_cookie(settings.AUTH_COOKIE_ACCESS, path=settings.AUTH_COOKIE_PATH)
    response.delete_cookie(settings.AUTH_COOKIE_REFRESH, path=settings.AUTH_COOKIE_PATH)
    return response
