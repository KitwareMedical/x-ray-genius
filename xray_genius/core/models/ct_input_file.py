from django.db import models
from s3_file_field.fields import S3FileField


class CTInputFile(models.Model):
    file = S3FileField()
