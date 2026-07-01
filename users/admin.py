"""Admin configuration for users app."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, EmailVerificationToken


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin."""

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            'Personal Info',
            {
                'fields': (
                    'first_name',
                    'last_name',
                    'avatar',
                    'bio',
                    'phone_number',
                    'location',
                    'website',
                )
            },
        ),
        (
            'Role & Permissions',
            {
                'fields': (
                    'role',
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                )
            },
        ),
        (
            'Employer Info',
            {
                'fields': (
                    'company_name',
                    'company_description',
                    'company_website',
                    'company_logo',
                    'is_approved_employer',
                    'approval_status',
                ),
                'classes': ('collapse',),
            },
        ),
        (
            'Timestamps',
            {
                'fields': ('date_joined', 'last_login', 'updated_at'),
                'classes': ('collapse',),
            },
        ),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role'),
        }),
    )

    list_display = (
        'email',
        'first_name',
        'last_name',
        'role',
        'is_active',
        'is_approved_employer',
        'date_joined',
    )
    list_filter = (
        'role',
        'is_active',
        'is_approved_employer',
        'approval_status',
        'date_joined',
    )
    search_fields = ('email', 'first_name', 'last_name', 'company_name')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login', 'updated_at')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin for UserProfile."""

    list_display = ('user', 'experience_years', 'created_at')
    search_fields = ('user__email', 'skills')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    """Admin for EmailVerificationToken."""

    list_display = ('user', 'is_used', 'created_at')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__email',)
    readonly_fields = ('token', 'created_at')
