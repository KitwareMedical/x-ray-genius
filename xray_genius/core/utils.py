import numpy as np
from scipy.stats import vonmises

from xray_genius.core.models import InputParameters


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
    sampled_angles_deg = np.mod(np.rad2deg(sampled_angles_rad), 360)  # Convert back to degrees
    return sampled_angles_deg


class ParameterSampler:
    samples: int
    carm_push_pull: float
    carm_head_foot_translation: float
    carm_raise_lower: float
    carm_alpha: float
    carm_beta: float

    def __init__(self, input_parameters: InputParameters, samples: int = 100) -> None:
        self.samples = samples
        self.carm_push_pull = input_parameters.carm_push_pull or sample_gaussian_distribution(
            mean=0, std_dev=10, num_samples=self.samples
        )
        self.carm_head_foot_translation = (
            input_parameters.carm_head_foot_translation
            or sample_gaussian_distribution(mean=0, std_dev=10, num_samples=self.samples)
        )
        self.carm_raise_lower = input_parameters.carm_raise_lower or sample_gaussian_distribution(
            mean=0, std_dev=10, num_samples=self.samples
        )
        self.carm_alpha = (
            [input_parameters.carm_alpha] * self.samples
            if input_parameters.carm_alpha
            else sample_von_mises_angles_degrees(
                mean_angle_deg=0, kappa=100, num_samples=self.samples
            )
        )
        self.carm_beta = (
            [input_parameters.carm_beta] * self.samples
            if input_parameters.carm_beta
            else sample_von_mises_angles_degrees(
                mean_angle_deg=0, kappa=100, num_samples=self.samples
            )
        )
