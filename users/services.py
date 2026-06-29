"""Service layer for user-related business logic."""

import uuid

from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import EmailVerificationToken


@transaction.atomic
def register_user(*, user_model, **validated_data):
    """Create a user and corresponding email verification token."""
    validated_data['username'] = validated_data['email']
    user = user_model.objects.create_user(**validated_data)
    EmailVerificationToken.objects.create(user=user, token=str(uuid.uuid4()))
    return user


@transaction.atomic
def verify_user_email(*, verification_token):
    """Mark the related user as active and consume the verification token."""
    user = verification_token.user
    user.is_active = True
    user.save(update_fields=['is_active'])

    verification_token.is_used = True
    verification_token.save(update_fields=['is_used'])
    return user


@transaction.atomic
def change_user_password(*, user, new_password):
    """Set a new password for the user."""
    user.set_password(new_password)
    user.save()
    return user


def authenticate_with_email(*, request, email, password):
    """Authenticate a user using the configured Django authentication backends."""
    user = authenticate(request=request, username=email, password=password)
    if user is None:
        raise serializers.ValidationError({'detail': 'Invalid credentials.'})
    if not user.is_active:
        raise serializers.ValidationError({'detail': 'Invalid credentials.'})
    return user


def issue_tokens_for_user(*, user):
    """Issue refresh/access tokens for the given user."""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@transaction.atomic
def approve_employer(*, user):
    """Approve an employer account."""
    user.is_approved_employer = True
    user.approval_status = 'approved'
    user.is_active = True
    user.save(update_fields=['is_approved_employer', 'approval_status', 'is_active'])
    return user


@transaction.atomic
def reject_employer(*, user):
    """Reject an employer account."""
    user.is_approved_employer = False
    user.approval_status = 'rejected'
    user.save(update_fields=['is_approved_employer', 'approval_status'])
    return user
