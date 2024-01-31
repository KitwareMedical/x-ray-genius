from django.db import models

from .session import Session


class InputParameters(models.Model):
    session = models.OneToOneField(Session, related_name='parameters', on_delete=models.CASCADE)

    carm_alpha = models.IntegerField(
        help_text='The desired alpha angulation of the C-arm in degrees.'
    )
    carm_beta = models.IntegerField(
        help_text='The desired secondary angulation of the C-arm in degrees.'
    )
    source_to_detector_distance = models.FloatField(
        help_text='The distance from the source to the detector in mm.'
    )
