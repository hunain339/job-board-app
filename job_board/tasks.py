"""Celery tasks for async operations."""

from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


@shared_task
def send_job_posted_email(job_id):
    """Send email when job is posted."""
    from jobs.models import Job
    
    try:
        job = Job.objects.get(id=job_id)
        
        html_message = render_to_string('emails/job_posted.html', {'job': job})
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=f'Your job "{job.title}" has been posted',
            message=plain_message,
            from_email='noreply@jobboard.com',
            recipient_list=[job.employer.email],
            html_message=html_message,
        )
    except Job.DoesNotExist:
        pass


@shared_task
def send_application_received_email(application_id):
    """Send email when application is received."""
    from applications.models import Application
    
    try:
        application = Application.objects.get(id=application_id)
        
        html_message = render_to_string(
            'emails/application_received.html',
            {'application': application}
        )
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=f'Application received for "{application.job.title}"',
            message=plain_message,
            from_email='noreply@jobboard.com',
            recipient_list=[application.job.employer.email],
            html_message=html_message,
        )
    except Application.DoesNotExist:
        pass


@shared_task
def send_application_status_change_email(application_id, new_status):
    """Send email when application status changes."""
    from applications.models import Application
    
    try:
        application = Application.objects.get(id=application_id)
        
        context = {
            'application': application,
            'new_status': new_status,
        }
        
        html_message = render_to_string('emails/status_changed.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=f'Your application status changed: {new_status}',
            message=plain_message,
            from_email='noreply@jobboard.com',
            recipient_list=[application.candidate.email],
            html_message=html_message,
        )
    except Application.DoesNotExist:
        pass
