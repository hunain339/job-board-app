#!/usr/bin/env python
"""
Management command to verify users (for development)
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import EmailVerificationToken

User = get_user_model()


class Command(BaseCommand):
    help = 'Auto-verify all unverified users (Development only)'

    def handle(self, *args, **options):
        unverified = User.objects.filter(is_active=False)
        count = 0

        for user in unverified:
            user.is_active = True
            user.save()
            count += 1
            self.stdout.write(f"✓ Verified: {user.email}")

            # Mark tokens as used
            tokens = EmailVerificationToken.objects.filter(user=user, is_used=False)
            tokens.update(is_used=True)

        self.stdout.write(self.style.SUCCESS(f"\n✅ Verified {count} user(s)"))
