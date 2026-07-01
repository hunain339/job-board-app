"""User models."""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import URLValidator
import uuid


class User(AbstractUser):
    """Custom User model with role-based access."""

    ROLE_CHOICES = (
        ('candidate', 'Candidate'),
        ('employer', 'Employer'),
        ('admin', 'Administrator'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='candidate')
    is_active = models.BooleanField(default=False)  # Email verification required
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True, max_length=500)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True, validators=[URLValidator()])

    # Employer-specific fields
    company_name = models.CharField(max_length=255, blank=True, null=True)
    company_description = models.TextField(blank=True, null=True)
    company_website = models.URLField(
        blank=True, null=True, validators=[
            URLValidator()])
    company_logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    is_approved_employer = models.BooleanField(default=False)
    approval_status = models.CharField(
        max_length=20,
        choices=(('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')),
        default='pending'
    )

    # Timestamps
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'role']

    class Meta:
        ordering = ['-date_joined']
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"

    def get_role_display(self):
        return dict(self.ROLE_CHOICES).get(self.role, self.role)

    @property
    def is_verified(self):
        return self.is_active

    @property
    def can_post_jobs(self):
        """Check if user can post jobs."""
        return self.role == 'employer' and self.is_approved_employer

    @property
    def can_apply_jobs(self):
        """Check if user can apply to jobs."""
        return self.role == 'candidate' and self.is_active


class UserProfile(models.Model):
    """Extended user profile for additional information."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    skills = models.TextField(blank=True, null=True, help_text="Comma-separated skills")
    experience_years = models.PositiveIntegerField(default=0)
    headline = models.CharField(max_length=200, blank=True, null=True)
    social_github = models.URLField(blank=True, null=True)
    social_linkedin = models.URLField(blank=True, null=True)
    social_twitter = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"Profile of {self.user.email}"


class EmailVerificationToken(models.Model):
    """Store email verification tokens."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='verification_token')
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Email Verification Token'
        verbose_name_plural = 'Email Verification Tokens'

    def __str__(self):
        return f"Verification token for {self.user.email}"
