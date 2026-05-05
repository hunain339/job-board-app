"""Core utility functions."""

import os
from django.core.files.base import ContentFile


def validate_resume_file(file):
    """
    Validate resume file type and size.
    Returns tuple: (is_valid, error_message)
    """
    from django.conf import settings
    
    # Check file size
    if file.size > settings.MAX_RESUME_SIZE:
        return False, f"File size exceeds {settings.MAX_RESUME_SIZE / (1024*1024):.1f}MB limit"
    
    # Check file extension
    ext = os.path.splitext(file.name)[1].lower().lstrip('.')
    if ext not in settings.ALLOWED_RESUME_EXTENSIONS:
        allowed = ', '.join(settings.ALLOWED_RESUME_EXTENSIONS)
        return False, f"Only {allowed} files are allowed"
    
    return True, None


def get_user_role_display(role):
    """Get human-readable role name."""
    role_map = {
        'candidate': 'Candidate',
        'employer': 'Employer',
        'admin': 'Administrator',
    }
    return role_map.get(role, role.title())


def send_email_task(subject, message, recipient_list):
    """
    Send email asynchronously.
    This would typically use Celery in production.
    """
    from django.core.mail import send_mail
    
    send_mail(
        subject,
        message,
        'noreply@jobboard.com',
        recipient_list,
        fail_silently=True,
    )
