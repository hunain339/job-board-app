"""Job models."""

import uuid

from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify

from core.models import BaseModel

JOB_CATEGORIES_CACHE_KEY = 'job_categories:all'
JOB_CATEGORIES_WEB_CACHE_KEY = 'job_categories_all'

User = get_user_model()


class JobCategory(models.Model):
    """Job categories."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = 'Job Category'
        verbose_name_plural = 'Job Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        cache.delete(JOB_CATEGORIES_CACHE_KEY)
        cache.delete(JOB_CATEGORIES_WEB_CACHE_KEY)

    def delete(self, *args, **kwargs):
        cache.delete(JOB_CATEGORIES_CACHE_KEY)
        cache.delete(JOB_CATEGORIES_WEB_CACHE_KEY)
        return super().delete(*args, **kwargs)


class Job(BaseModel):
    """Job posting model."""

    JOB_TYPE_CHOICES = (
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('contract', 'Contract'),
        ('freelance', 'Freelance'),
        ('internship', 'Internship'),
    )

    EXPERIENCE_LEVEL_CHOICES = (
        ('entry', 'Entry Level'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior'),
        ('lead', 'Lead'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    category = models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True, related_name='jobs')
    location = models.CharField(max_length=255)
    is_remote = models.BooleanField(default=False)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=10, default='USD')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL_CHOICES)
    required_skills = models.TextField(help_text="Comma-separated skills")
    employer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs')
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0, db_index=True)
    applications_count = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Job'
        verbose_name_plural = 'Jobs'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['employer']),
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
            models.Index(fields=['job_type']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['-views_count']),
            models.Index(fields=['-created_at', 'is_active']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            # Ensure unique slug
            while Job.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)



    @property
    def salary_range(self):
        """Get formatted salary range."""
        if self.salary_min and self.salary_max:
            return f"{self.currency} {self.salary_min:,.0f} - {self.salary_max:,.0f}"
        elif self.salary_min:
            return f"{self.currency} {self.salary_min:,.0f}+"
        elif self.salary_max:
            return f"Up to {self.currency} {self.salary_max:,.0f}"
        return "Not specified"

    @property
    def is_urgent(self):
        """Check if job is recently posted."""
        from django.utils import timezone
        from datetime import timedelta
        return timezone.now() - self.created_at < timedelta(days=3)


class JobSavedByUser(models.Model):
    """Track saved jobs by candidates."""

    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_jobs')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='saved_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('candidate', 'job')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.candidate.email} saved {self.job.title}"
