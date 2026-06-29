"""Service layer for application business logic."""

from django.db import transaction

from .models import Application, ApplicationNote, ApplicationStatusHistory
from jobs.services import increment_job_applications, decrement_job_applications


@transaction.atomic
def create_application(*, candidate, job, **validated_data):
    """Create an application and update the related job counter."""
    application = Application.objects.create(candidate=candidate, job=job, **validated_data)
    increment_job_applications(job=job)
    return application


@transaction.atomic
def update_application_status(*, application, changed_by, reason='', **validated_data):
    """Update application fields and append status history on status changes."""
    old_status = application.status
    for field, value in validated_data.items():
        setattr(application, field, value)
    application.save()

    if old_status != application.status:
        ApplicationStatusHistory.objects.create(
            application=application,
            old_status=old_status,
            new_status=application.status,
            changed_by=changed_by,
            reason=reason,
        )

    return application


@transaction.atomic
def add_application_note(*, application, employer, note):
    """Add an employer note to an application."""
    return ApplicationNote.objects.create(
        application=application,
        employer=employer,
        note=note,
    )


@transaction.atomic
def withdraw_application(*, application):
    """Delete an application and update the related job counter."""
    job = application.job
    application.delete()
    decrement_job_applications(job=job)
