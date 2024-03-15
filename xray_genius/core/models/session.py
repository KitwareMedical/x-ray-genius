import uuid

from django.contrib.auth.models import User
from django.db import models
from django_extensions.db.fields import CreationDateTimeField

from .ct_input_file import CTInputFile


class Session(models.Model):
    class Status(models.TextChoices):
        NOT_STARTED = 'not-started', 'Not Started'
        RUNNING = 'running', 'Running'
        PROCESSED = 'processed', 'Processed'
        CANCELLED = 'cancelled', 'Cancelled'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = CreationDateTimeField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    input_scan = models.ForeignKey(CTInputFile, on_delete=models.CASCADE, related_name='sessions')
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.NOT_STARTED)

    output_images_zip = models.FileField(upload_to='output_images/zips', null=True, blank=True)
