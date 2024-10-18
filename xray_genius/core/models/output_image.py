from django.db import models
from django.db.models import signals
from django.dispatch import receiver
from django_extensions.db.fields import CreationDateTimeField

from .session import Session


class OutputImage(models.Model):
    created = CreationDateTimeField()
    image = models.ImageField(upload_to='output_images')
    thumbnail = models.ImageField(upload_to='output_images/thumbnails')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='output_images')

    # Parameters for this specific output image
    carm_push_pull = models.FloatField(null=True, blank=True)
    carm_head_foot_translation = models.FloatField(null=True, blank=True)
    carm_raise_lower = models.FloatField(null=True, blank=True)
    carm_alpha = models.FloatField(
        null=True, blank=True, help_text='The desired alpha angulation of the C-arm in degrees.'
    )
    carm_beta = models.FloatField(
        null=True, blank=True, help_text='The desired secondary angulation of the C-arm in degrees.'
    )


@receiver(signals.pre_delete, sender=OutputImage)
def delete_file(sender: type[OutputImage], instance: OutputImage, **kwargs):
    instance.image.delete(save=False)
    instance.thumbnail.delete(save=False)
