from __future__ import annotations

import uuid

from django.contrib.auth.models import User
from django.db import models
from django_extensions.db.fields import CreationDateTimeField

from .ct_input_file import CTInputFile


class SessionManager(models.Manager):
    def get_queryset(self) -> models.QuerySet[Session]:
        # Hide sessions that are being deleted
        return super().get_queryset().exclude(status=Session.Status.DELETING)


class Session(models.Model):
    objects = SessionManager()

    class Status(models.TextChoices):
        NOT_STARTED = 'not-started', 'Not Started'
        QUEUED = 'queued', 'Queued'
        RUNNING = 'running', 'Running'
        PROCESSED = 'processed', 'Processed'
        CANCELLED = 'cancelled', 'Cancelling'
        DELETING = 'deleting', 'Deleting'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = CreationDateTimeField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    input_scan = models.ForeignKey(CTInputFile, on_delete=models.CASCADE, related_name='sessions')
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.NOT_STARTED)
    celery_task_id = models.CharField(max_length=255, null=True, blank=True)

    output_images_zip = models.FileField(upload_to='output_images/zips', null=True, blank=True)
