from pathlib import Path

from django.contrib.auth.models import User
from django.core.management import call_command
import pytest


@pytest.mark.django_db
def test_test_data_fixture() -> None:
    """This test ensures the `testdata` fixture can be loaded successfully."""
    User.objects.create_user(username='test', password='test', id=1)
    call_command('loaddata', 'testdata')


@pytest.mark.django_db
def test_sample_data_fixture() -> None:
    """This test ensures the `sampledata` fixture can be loaded successfully."""
    call_command('loaddata', 'sampledata')


@pytest.mark.django_db
def test_load_test_data(monkeypatch: pytest.MonkeyPatch) -> None:
    """This test ensures the `load_test_data` command can be run successfully."""
    from girder_client import GirderClient

    # Monkeypatch the downloadFile method to mock the download of a file, so that we're not hitting
    # data.kitware.com every time we run the test.
    monkeypatch.setattr(
        GirderClient,
        'downloadFile',
        lambda *_args, **kwargs: Path(kwargs['path']).write_text('test'),
    )

    call_command('load_test_data')
