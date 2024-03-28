from pathlib import Path

from django.db import models
from django.db.models import signals
from django.dispatch import receiver
from s3_file_field.fields import S3FileField


class CTInputFile(models.Model):
    file = S3FileField()

    @property
    def filename(self):
        return Path(self.file.name).name


@receiver(signals.post_delete, sender=CTInputFile)
def delete_file(sender: type[CTInputFile], instance: CTInputFile, **kwargs):
    instance.file.delete()
