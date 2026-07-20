from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import OTP, User


class UserAdmin(BaseUserAdmin):
    model = User
    ordering = ['-date_joined']
    list_display = ['email', 'name', 'is_active', 'is_verified', 'is_staff']
    list_filter = ['is_active', 'is_verified', 'is_staff']
    search_fields = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name',)}),
        ('Permissions', {'fields': ('is_active', 'is_verified', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2', 'is_active', 'is_verified', 'is_staff'),
        }),
    )
    readonly_fields = ['date_joined']


admin.site.register(User, UserAdmin)
admin.site.register(OTP)
