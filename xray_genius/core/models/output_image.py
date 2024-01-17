from django.db import models

from .session import Session


class OutputImage(models.Model):
    file = models.FileField()
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='output_images')
    parameters = models.JSONField(null=True, blank=True)  # TODO: what are these?
