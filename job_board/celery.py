"""Celery application configuration for job_board."""

import os

from celery import Celery

# Set the default Django settings module for the Celery program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "job_board.settings")

app = Celery("job_board")

# Use Django settings prefixed with CELERY_
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks in installed apps
app.autodiscover_tasks()
