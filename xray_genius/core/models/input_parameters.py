from django.db import models

from .session import Session


class InputParameters(models.Model):
    session = models.OneToOneField(Session, related_name='parameters', on_delete=models.CASCADE)

    # Required parameter
    source_to_detector_distance = models.FloatField(
        help_text='The distance from the source to the detector in mm.'
    )

    # Optional parameters; these are randomized if not provided
    carm_push_pull = models.FloatField(null=True, blank=True)
    carm_head_foot_translation = models.FloatField(null=True, blank=True)
    carm_raise_lower = models.FloatField(null=True, blank=True)
    carm_alpha = models.FloatField(
        null=True, blank=True, help_text='The desired alpha angulation of the C-arm in degrees.'
    )
    carm_beta = models.FloatField(
        null=True, blank=True, help_text='The desired secondary angulation of the C-arm in degrees.'
    )
