from pathlib import Path

from django.db import models
from django.db.models import signals
from django.dispatch import receiver
from django_extensions.db.fields import CreationDateTimeField
from s3_file_field.fields import S3FileField

from .sample_dataset import SampleDatasetFile


class CTInputFile(models.Model):
    created = CreationDateTimeField()

    file = S3FileField()

    def __str__(self) -> str:
        return self.filename

    @property
    def filename(self):
        return Path(self.file.name).name


@receiver(signals.post_delete, sender=CTInputFile)
def delete_file(sender: type[CTInputFile], instance: CTInputFile, **kwargs):
    # Only delete the associated S3 blob if it is not part of a sample dataset
    if not SampleDatasetFile.objects.filter(file=instance.file).exists():
        instance.file.delete()
