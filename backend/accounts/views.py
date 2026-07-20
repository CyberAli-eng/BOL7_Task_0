from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import OTP, User
from .serializers import (
    LoginSerializer,
    ProfileSerializer,
    RegisterSerializer,
    ResendOtpSerializer,
    VerifyOtpSerializer,
)
from .utils import clear_auth_cookies, send_otp_email, set_auth_cookies


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        otp_obj = OTP.create_for_user(user)
        send_otp_email(user, otp_obj.code)

        return Response(
            {
                'message': 'Registration successful. An OTP has been sent to your email.',
                'email': user.email,
            },
            status=status.HTTP_201_CREATED,
        )


class VerifyOtpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        otp_obj = serializer.validated_data['otp_obj']

        otp_obj.is_used = True
        otp_obj.save(update_fields=['is_used'])

        user.is_active = True
        user.is_verified = True
        user.save(update_fields=['is_active', 'is_verified'])

        return Response({'message': 'Email verified successfully. You can now log in.'}, status=status.HTTP_200_OK)


class ResendOtpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResendOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        user = User.objects.get(email=email)
        otp_obj = OTP.create_for_user(user)
        send_otp_email(user, otp_obj.code)

        return Response({'message': 'A new OTP has been sent to your email.'}, status=status.HTTP_200_OK)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        response = Response(
            {
                'message': 'Login successful.',
                'user': ProfileSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )
        set_auth_cookies(response, access, refresh)
        return response


class TokenRefreshCookieView(APIView):
    """Issues a new access token using the refresh token stored in cookies."""

    permission_classes = [AllowAny]

    def post(self, request):
        raw_refresh = request.COOKIES.get(settings.AUTH_COOKIE_REFRESH)
        if not raw_refresh:
            return Response({'detail': 'Refresh token not found.'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh = RefreshToken(raw_refresh)
            new_access = refresh.access_token

            response = Response({'message': 'Token refreshed.'}, status=status.HTTP_200_OK)

            if settings.SIMPLE_JWT.get('ROTATE_REFRESH_TOKENS'):
                # Blacklist the old refresh token and issue a new one.
                user_id = refresh['user_id']
                if settings.SIMPLE_JWT.get('BLACKLIST_AFTER_ROTATION'):
                    try:
                        refresh.blacklist()
                    except AttributeError:
                        pass
                user = User.objects.get(id=user_id)
                new_refresh = RefreshToken.for_user(user)
                set_auth_cookies(response, new_access, new_refresh)
            else:
                response.set_cookie(
                    key=settings.AUTH_COOKIE_ACCESS,
                    value=str(new_access),
                    httponly=settings.AUTH_COOKIE_HTTPONLY,
                    secure=settings.AUTH_COOKIE_SECURE,
                    samesite=settings.AUTH_COOKIE_SAMESITE,
                    path=settings.AUTH_COOKIE_PATH,
                )

            return response
        except TokenError:
            return Response({'detail': 'Invalid or expired refresh token.'}, status=status.HTTP_401_UNAUTHORIZED)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(ProfileSerializer(request.user).data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        raw_refresh = request.COOKIES.get(settings.AUTH_COOKIE_REFRESH)
        if raw_refresh:
            try:
                token = RefreshToken(raw_refresh)
                token.blacklist()
            except TokenError:
                pass

        response = Response({'message': 'Logged out successfully.'}, status=status.HTTP_200_OK)
        clear_auth_cookies(response)
        return response
