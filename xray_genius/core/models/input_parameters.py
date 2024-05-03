import math

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .session import Session

# The default is the default sensor width/height from deepdrr.device.mobile_carm.MobileCArm
DEFAULT_SENSOR_SIZE = 1536


def concentration_to_degrees(conc: float) -> float:
    return math.sqrt(1 / conc) / (math.pi / 180)


class InputParameters(models.Model):
    session = models.OneToOneField(Session, related_name='parameters', on_delete=models.CASCADE)

    # Required parameter
    source_to_detector_distance = models.FloatField(
        help_text='The distance from the source to the detector in mm.'
    )

    # Optional parameters; these are randomized if not provided
    carm_push_pull_translation = models.FloatField(null=False, blank=False, default=0)
    carm_head_foot_translation = models.FloatField(null=False, blank=False, default=0)
    carm_raise_lower_translation = models.FloatField(null=False, blank=False, default=0)
    carm_push_pull_std_dev = models.FloatField(null=True, blank=True)
    carm_head_foot_std_dev = models.FloatField(null=True, blank=True)
    carm_raise_lower_std_dev = models.FloatField(null=True, blank=True)
    carm_alpha = models.FloatField(
        default=0, blank=False, help_text='The desired alpha angulation of the C-arm in degrees.'
    )
    carm_alpha_kappa = models.FloatField(
        null=True,
        blank=True,
        help_text='The desired kappa value to use in the von Mises distriubtion for C-arm alpha.',
    )
    carm_beta = models.FloatField(
        default=0,
        blank=False,
        help_text='The desired secondary angulation of the C-arm in degrees.',
    )
    carm_beta_kappa = models.FloatField(
        null=True,
        blank=True,
        help_text='The desired kappa value to use in the von Mises distriubtion for C-arm beta.',
    )
    num_samples = models.PositiveIntegerField(
        default=100,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
        help_text='The number of x-rays to generate with DeepDRR.',
    )
    # Defaults to a 9" diameter
    detector_diameter = models.FloatField(help_text='The detector diameter in mm.', default=228.6)

    @property
    def sensor_pixel_pitch(self):
        """The sensor pixel pitch."""
        return self.detector_diameter / DEFAULT_SENSOR_SIZE

    @property
    def carm_alpha_kappa_degrees(self):
        if self.carm_alpha_kappa is None:
            return None
        return concentration_to_degrees(self.carm_alpha_kappa)

    @property
    def carm_beta_kappa_degrees(self):
        if self.carm_beta_kappa is None:
            return None
        return concentration_to_degrees(self.carm_beta_kappa)
