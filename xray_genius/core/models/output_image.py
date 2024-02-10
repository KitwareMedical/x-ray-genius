from functools import cached_property

from PIL import Image
from django.db import models

from .session import Session


class OutputImage(models.Model):
    image = models.ImageField(upload_to='output_images')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='output_images')
    parameters = models.JSONField(null=True, blank=True)  # TODO: what are these?

    @cached_property
    def thumbnail(self) -> Image.Image:
        img = Image.open(self.image)
        img.thumbnail((64, 64))
        return img
