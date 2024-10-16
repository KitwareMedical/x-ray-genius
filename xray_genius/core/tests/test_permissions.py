from django.test import Client
from django.urls import reverse
import pytest

from xray_genius.core.models import Session


@pytest.mark.django_db()
def test_dashboard_permissions(user, user_factory, session_factory, client: Client):
    client.force_login(user)

    owned_sessions = [session_factory(owner=user) for _ in range(10)]
    not_owned_sessions = [session_factory(owner=user_factory()) for _ in range(10)]

    response = client.get(reverse('dashboard'))

    # Make sure non-owned sessions are not displayed
    assert set(response.context['sessions']).intersection(not_owned_sessions) == set()

    # Make sure owned sessions are displayed
    assert set(response.context['sessions']).intersection(owned_sessions) == set(owned_sessions)


@pytest.mark.django_db()
@pytest.mark.parametrize(
    ('view_name', 'http_method', 'expected_status'),
    [
        ('download-input-ct-file', 'get', 302),
        ('viewer', 'get', 200),
        ('initiate-batch-run', 'post', 302),
    ],
)
def test_permissions_views(
    session_factory,
    user,
    user_factory,
    client: Client,
    view_name: str,
    http_method: str,
    expected_status: int,
):
    client.force_login(user)

    # Make sure the user can't access other users' sessions
    not_owned_session: Session = session_factory(owner=user_factory())
    response = getattr(client, http_method)(
        reverse(view_name, kwargs={'session_pk': not_owned_session.pk})
    )
    assert response.status_code == 404

    # Make sure the user can access their own sessions
    owned_session: Session = session_factory(owner=user)
    response = getattr(client, http_method)(
        reverse(view_name, kwargs={'session_pk': owned_session.pk})
    )
    assert response.status_code == expected_status


@pytest.mark.django_db()
def test_permissions_parameters_rest_endpoint(
    user, user_factory, ct_input_file_factory, client: Client
):
    client.force_login(user)
    source_to_detector_distance = 300
    carm_alpha = 45
    carm_beta = 30

    # Make sure the user can't modify other users' session parameters
    not_owned_session: Session = Session.objects.create(
        owner=user_factory(), input_scan=ct_input_file_factory()
    )
    response = client.post(
        reverse('api-0.1.0:set_parameters', kwargs={'session_pk': not_owned_session.pk}),
        content_type='application/json',
        data={
            'carm_alpha': carm_alpha,
            'carm_beta': carm_beta,
            'source_to_detector_distance': source_to_detector_distance,
        },
    )
    assert response.status_code == 404

    # Make sure the user can modify their own session parameters
    owned_session: Session = Session.objects.create(owner=user, input_scan=ct_input_file_factory())
    response = client.post(
        reverse('api-0.1.0:set_parameters', kwargs={'session_pk': owned_session.pk}),
        content_type='application/json',
        data={
            'carm_alpha': carm_alpha,
            'carm_beta': carm_beta,
            'source_to_detector_distance': source_to_detector_distance,
        },
    )
    assert response.status_code == 200
    assert owned_session.parameters.carm_alpha == carm_alpha
    assert owned_session.parameters.carm_beta == carm_beta
    assert owned_session.parameters.source_to_detector_distance == source_to_detector_distance
