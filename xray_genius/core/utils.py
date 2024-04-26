from collections.abc import Collection

import numpy as np
from scipy.stats import vonmises

from xray_genius.core.models import InputParameters

DEFAULT_MEAN = 0
DEFAULT_STD_DEV = 10


def sample_gaussian_distribution(mean: float, std_dev: float, num_samples=1000):
    """
    Sample values from a Gaussian distribution and plot a histogram.

    Parameters:
    - mean: The mean (μ) of the Gaussian distribution.
    - std_dev: The standard deviation (σ) of the Gaussian distribution.
    - num_samples: The number of samples to generate. Default is 1000.

    Returns:
    - A numpy array of sampled values.
    """
    # Random sampling from a Gaussian distribution
    sampled_values = np.random.normal(mean, std_dev, num_samples)

    return sampled_values


def sample_von_mises_angles_degrees(mean_angle_deg: float, kappa: float, num_samples: int = 1):
    """
    Sample angles from a von Mises distribution around a mean angle in degrees.

    Parameters:
    - mean_angle_deg: Mean angle in degrees.
    - kappa: Concentration parameter (κ), analogous to 1/variance in a Gaussian.
             Higher kappa means less spread.
    - num_samples: Number of angles to sample.

    Returns:
    - An array of sampled angles in degrees, normalized to [0, 360).
    """
    mean_angle_rad = np.deg2rad(mean_angle_deg)  # Convert mean angle to radians
    sampled_angles_rad = vonmises.rvs(kappa, loc=mean_angle_rad, size=num_samples)  # Sample
    sampled_angles_deg = np.rad2deg(sampled_angles_rad)
    return sampled_angles_deg


def sample_gaussian_with_defaults(
    translation: float | None,
    std_dev: float | None,
    num_samples=1000,
    default_mean=DEFAULT_MEAN,
    default_std_dev=DEFAULT_STD_DEV,
):
    """
    Sample values from a Gaussian distribution with default values.

    Behavior:
    - translation is not None and std_dev is not None: sample the gaussian
    - translation is     None and std_dev is not None: sample the gaussian
    - translation is not None and std_dev is     None: return translation
    - translation is     None and std_dev is     None: sample the gaussian

    Parameters:
    - translation: the mean of the gaussian.
    - std_dev: the standard deviation of the gaussian.

    Returns:
    - A numpy array of sampled values.
    """
    if translation is not None and std_dev is None:
        return [translation] * num_samples

    return sample_gaussian_distribution(
        translation or default_mean, std_dev or default_std_dev, num_samples
    )


class ParameterSampler:
    samples: int
    carm_push_pull_translation: Collection[float]
    carm_head_foot_translation: Collection[float]
    carm_raise_lower_translation: Collection[float]
    carm_alpha: Collection[float]
    carm_beta: Collection[float]

    def __init__(self, input_parameters: InputParameters) -> None:
        self.samples = input_parameters.num_samples
        self.carm_push_pull_translation = sample_gaussian_with_defaults(
            input_parameters.carm_push_pull_translation,
            input_parameters.carm_push_pull_std_dev,
            num_samples=self.samples,
        )
        self.carm_head_foot_translation = sample_gaussian_with_defaults(
            input_parameters.carm_head_foot_translation,
            input_parameters.carm_head_foot_std_dev,
            num_samples=self.samples,
        )
        self.carm_raise_lower_translation = sample_gaussian_with_defaults(
            input_parameters.carm_raise_lower_translation,
            input_parameters.carm_raise_lower_std_dev,
            num_samples=self.samples,
        )
        self.carm_alpha = (
            [input_parameters.carm_alpha] * self.samples
            if input_parameters.carm_alpha is not None
            else sample_von_mises_angles_degrees(
                mean_angle_deg=0, kappa=input_parameters.carm_alpha_kappa, num_samples=self.samples
            )
        )
        self.carm_beta = (
            [input_parameters.carm_beta] * self.samples
            if input_parameters.carm_beta is not None
            else sample_von_mises_angles_degrees(
                mean_angle_deg=0, kappa=input_parameters.carm_beta_kappa, num_samples=self.samples
            )
        )
