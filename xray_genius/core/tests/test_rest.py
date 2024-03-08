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
