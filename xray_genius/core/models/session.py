from __future__ import annotations

import uuid

from django.contrib.auth.models import User
from django.db import models
from django.db.models.functions import Extract, Now
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
            .alias(
                seconds_running=Extract(Now(), 'epoch') - Extract(models.F('started'), 'epoch'),
                # Assume each generation takes 15 seconds at the most
                seconds_expected=models.F('parameters__num_samples') * 15,
            )
            .filter(
                status__in=[Session.Status.QUEUED, Session.Status.RUNNING],
                seconds_running__gt=models.F('seconds_expected'),
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
