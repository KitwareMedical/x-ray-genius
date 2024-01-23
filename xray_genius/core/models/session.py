import uuid

from django.contrib.auth.models import User
from django.db import models
from django_extensions.db.fields import CreationDateTimeField

from .ct_input_file import CTInputFile


class Session(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = CreationDateTimeField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    input_scan = models.ForeignKey(CTInputFile, on_delete=models.CASCADE, related_name='sessions')
    parameters = models.JSONField(null=True, blank=True)  # TODO: what are these?
