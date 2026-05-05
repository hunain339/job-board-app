"""Application models."""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from core.models import BaseModel
import uuid

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
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])]
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
    
    def save(self, *args, **kwargs):
        """Update job applications count on save."""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # Increment applications count
            self.job.applications_count += 1
            self.job.save(update_fields=['applications_count'])
    
    def delete(self, *args, **kwargs):
        """Update job applications count on delete."""
        job = self.job
        super().delete(*args, **kwargs)
        
        # Decrement applications count
        if job.applications_count > 0:
            job.applications_count -= 1
            job.save(update_fields=['applications_count'])


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
