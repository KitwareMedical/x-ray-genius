from __future__ import annotations

from datetime import timedelta
import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django_extensions.db.fields import CreationDateTimeField

from .ct_input_file import CTInputFile


class SessionManager(models.Manager):
    def get_queryset(self) -> models.QuerySet[Session]:
        # Hide sessions that are being deleted
        return super().get_queryset().exclude(status=Session.Status.DELETING)


class StuckSessionsManager(models.Manager):
    def get_queryset(self) -> models.QuerySet[Session]:
        # Get sessions that have been running or queued for too long
        return (
            super()
            .get_queryset()
            .filter(
                status__in=[Session.Status.QUEUED, Session.Status.RUNNING],
                started__lt=timezone.now() - timedelta(seconds=settings.SESSION_TIMEOUT),
            )
        )


class Session(models.Model):
    class Status(models.TextChoices):
        NOT_STARTED = 'not-started', 'Not Started'
        QUEUED = 'queued', 'Queued'
        RUNNING = 'running', 'Running'
        PROCESSED = 'processed', 'Processed'
        CANCELLED = 'cancelled', 'Cancelling'
        DELETING = 'deleting', 'Deleting'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = CreationDateTimeField()
    started = models.DateTimeField(
        help_text='When the session started processing (i.e. when it went into the QUEUED state)',
        null=True,
        blank=True,
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    input_scan = models.ForeignKey(CTInputFile, on_delete=models.CASCADE, related_name='sessions')
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.NOT_STARTED)
    celery_task_id = models.CharField(max_length=255, default='')

    output_images_zip = models.FileField(upload_to='output_images/zips', null=True, blank=True)

    objects = SessionManager()
    stuck_objects = StuckSessionsManager()

    def __str__(self) -> str:
        return f'Session {self.id} ({self.status})'
