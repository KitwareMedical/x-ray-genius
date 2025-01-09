from datetime import timedelta

from django.utils import timezone
import pytest

from xray_genius.core.models import Session


@pytest.mark.django_db
def test_stuck_session_detection(user, session_factory) -> None:
    # 1 sample running for less than a second should not be considered stuck
    session: Session = session_factory(
        owner=user, status=Session.Status.RUNNING, parameters__num_samples=1
    )
    assert Session.stuck_objects.count() == 0
    session.delete()

    # 1 sample running for 10 minutes should be considered stuck
    session: Session = session_factory(
        owner=user,
        status=Session.Status.RUNNING,
        started=timezone.now() - timedelta(minutes=10),
        parameters__num_samples=1,
    )
    assert Session.stuck_objects.count() == 1
    session.delete()

    # 100 samples running for 10 minutes should not be considered stuck
    session: Session = session_factory(
        owner=user,
        status=Session.Status.RUNNING,
        started=timezone.now() - timedelta(minutes=10),
        parameters__num_samples=100,
    )
    assert Session.stuck_objects.count() == 0
    session.delete()

    # 100 samples running for 1000 minutes should be considered stuck
    session: Session = session_factory(
        owner=user,
        status=Session.Status.RUNNING,
        started=timezone.now() - timedelta(minutes=1000),
        parameters__num_samples=100,
    )
    assert Session.stuck_objects.count() == 1
    session.delete()
