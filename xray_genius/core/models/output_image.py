from django.db import models

from .session import Session


class OutputImage(models.Model):
    image = models.ImageField(upload_to='output_images')
    thumbnail = models.ImageField(upload_to='output_images/thumbnails')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='output_images')
    parameters = models.JSONField(null=True, blank=True)  # TODO: what are these?
