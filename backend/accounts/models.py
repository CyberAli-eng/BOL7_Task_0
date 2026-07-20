import random
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)
        return self.create_user(email, name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model. Email is used to log in instead of a username.

    A newly registered user is inactive (is_active=False) until they verify
    the OTP sent to their email. is_verified mirrors that state and is
    exposed to the frontend on the profile page.
    """

    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email


def default_otp_expiry():
    return timezone.now() + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)


class OTP(models.Model):
    """One-time password used for email verification.

    Every time a new OTP is generated for a user, older unused OTPs for
    that user are invalidated so only the most recent one is valid.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=default_otp_expiry)
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} - {self.code}'

    @staticmethod
    def generate_code():
        return f'{random.randint(0, 999999):06d}'

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    def is_valid(self, code):
        return (not self.is_used) and (not self.is_expired) and (self.code == code)

    @classmethod
    def create_for_user(cls, user):
        # Invalidate previous unused OTPs so only the latest is usable.
        cls.objects.filter(user=user, is_used=False).update(is_used=True)
        return cls.objects.create(user=user, code=cls.generate_code())
