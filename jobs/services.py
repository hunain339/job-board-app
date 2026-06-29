"""Service layer for jobs business logic."""

from django.core.cache import cache
from django.db import transaction
from django.db.models import F

from .models import Job, JobSavedByUser

JOB_CATEGORIES_CACHE_KEY = "job_categories:all"
JOB_CATEGORIES_WEB_CACHE_KEY = "job_categories_all"


def invalidate_job_category_caches():
    """Invalidate all cache entries derived from job categories."""
    cache.delete(JOB_CATEGORIES_CACHE_KEY)
    cache.delete(JOB_CATEGORIES_WEB_CACHE_KEY)


@transaction.atomic
def create_job(*, employer, **validated_data):
    """Create a job owned by the given employer."""
    return Job.objects.create(employer=employer, **validated_data)


@transaction.atomic
def update_job(*, job, **validated_data):
    """Update a job with validated fields."""
    for field, value in validated_data.items():
        setattr(job, field, value)
    job.save()
    return job


@transaction.atomic
def soft_delete_job(*, job):
    """Soft delete a job by marking it inactive."""
    job.is_active = False
    job.save(update_fields=['is_active', 'updated_at'])
    return job


@transaction.atomic
def save_job_for_candidate(*, candidate, job):
    """Save a job for a candidate if it was not already saved."""
    return JobSavedByUser.objects.get_or_create(candidate=candidate, job=job)


@transaction.atomic
def unsave_job_for_candidate(*, candidate, job):
    """Remove a saved job for a candidate."""
    return JobSavedByUser.objects.filter(candidate=candidate, job=job).delete()


@transaction.atomic
def increment_job_views(*, job):
    """Atomically increment job views and keep the instance in sync."""
    Job.objects.filter(id=job.id).update(views_count=F('views_count') + 1)
    job.refresh_from_db(fields=['views_count'])
    return job


@transaction.atomic
def increment_job_applications(*, job):
    """Atomically increment job application counter."""
    Job.objects.filter(id=job.id).update(applications_count=F('applications_count') + 1)


@transaction.atomic
def decrement_job_applications(*, job):
    """Atomically decrement job application counter without going negative."""
    Job.objects.filter(id=job.id, applications_count__gt=0).update(
        applications_count=F('applications_count') - 1
    )
