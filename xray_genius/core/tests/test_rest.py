from django.forms import model_to_dict
from django.test import Client
from django.urls import reverse
import pytest

from xray_genius.core.models import InputParameters, Session


@pytest.mark.django_db()
@pytest.mark.parametrize(
    'samples',
    [-1, 101, 1000],
)
def test_num_samples_invalid(user, session_factory, client: Client, samples: int):
    client.force_login(user)

    session: Session = session_factory(owner=user, parameters=None)

    response = client.post(
        reverse('api-0.1.0:set_parameters', kwargs={'session_pk': session.pk}),
        {
            'source_to_detector_distance': 1000,
            'num_samples': samples,
        },
    )
    assert response.status_code == 400
    assert not InputParameters.objects.filter(session=session).exists()


@pytest.mark.django_db()
@pytest.mark.parametrize(
    'samples',
    [0, 1, 50, 100],
)
def test_num_samples_valid(user, session_factory, client: Client, samples: int):
    client.force_login(user)

    session: Session = session_factory(owner=user, parameters=None)

    response = client.post(
        reverse('api-0.1.0:set_parameters', kwargs={'session_pk': session.pk}),
        content_type='application/json',
        data={
            'source_to_detector_distance': 1000,
            'num_samples': samples,
        },
    )
    assert response.status_code == 200
    assert session.parameters.num_samples == samples


@pytest.mark.django_db()
def test_num_samples_valid_missing(user, session_factory, client: Client):
    client.force_login(user)

    session: Session = session_factory(owner=user, parameters=None)

    response = client.post(
        reverse('api-0.1.0:set_parameters', kwargs={'session_pk': session.pk}),
        content_type='application/json',
        data={
            'source_to_detector_distance': 1000,
            # Missing num_samples here.
        },
    )
    assert response.status_code == 200
    assert session.parameters.num_samples == 100


@pytest.mark.django_db()
def test_set_parameters_rest(user, session_factory, client: Client):
    client.force_login(user)

    session: Session = session_factory(owner=user, parameters=None)

    param_data = {
        'source_to_detector_distance': 1800,
        'carm_push_pull_translation': 0.0,
        'carm_head_foot_translation': -90.9,
        'carm_raise_lower_translation': -722.4,
        'carm_push_pull_std_dev': 10.0,
        'carm_head_foot_std_dev': 10.0,
        'carm_raise_lower_std_dev': 10.0,
        'carm_alpha': 178.578,
        'carm_alpha_kappa': 3282.806,
        'carm_beta': -0.7402,
        'carm_beta_kappa': 3282.806,
        'num_samples': 10,
        'detector_diameter': 228.6,
    }

    response = client.post(
        reverse('api-0.1.0:set_parameters', kwargs={'session_pk': session.pk}),
        content_type='application/json',
        data=param_data,
    )
    assert response.status_code == 200

    parameters = InputParameters.objects.get(session=session)

    # Ensure all parameters got accepted
    assert model_to_dict(parameters, exclude=['id', 'session']) == param_data
