"""Application models."""

import uuid

from django.contrib.auth import get_user_model
from django.db import models

from core.models import BaseModel
from .validators import SecureFileValidator

User = get_user_model()


class Application(BaseModel):
    """Job application model."""

    STATUS_CHOICES = (
        ('applied', 'Applied'),
        ('reviewing', 'Under Review'),
        ('interview', 'Interview Scheduled'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey('jobs.Job', on_delete=models.CASCADE, related_name='applications')
    resume = models.FileField(
        upload_to='resumes/',
        validators=[SecureFileValidator(allowed_extensions=['pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'], max_size_mb=5)]
    )
    cover_letter = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    rejection_reason = models.TextField(blank=True, null=True)
    rating = models.IntegerField(default=0, choices=[(i, str(i)) for i in range(0, 6)])
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Application'
        verbose_name_plural = 'Applications'
        unique_together = ('candidate', 'job')
        indexes = [
            models.Index(fields=['candidate', 'status']),
            models.Index(fields=['job', 'status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.candidate.email} applied to {self.job.title}"

    @property
    def is_recent(self):
        """Check if application is recent."""
        from django.utils import timezone
        from datetime import timedelta
        return timezone.now() - self.created_at < timedelta(days=7)




class ApplicationNote(models.Model):
    """Notes on applications by employer."""

    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='employer_notes')
    employer = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Application Note'
        verbose_name_plural = 'Application Notes'

    def __str__(self):
        return f"Note on {self.application}"


class ApplicationStatusHistory(models.Model):
    """Track status changes for applications."""

    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=20, choices=Application.STATUS_CHOICES)
    new_status = models.CharField(max_length=20, choices=Application.STATUS_CHOICES)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-changed_at']
        verbose_name = 'Application Status History'
        verbose_name_plural = 'Application Status Histories'

    def __str__(self):
        return f"{self.application} status changed from {self.old_status} to {self.new_status}"
