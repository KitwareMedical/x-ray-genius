from django.contrib.auth.models import User
from django.core.management import call_command
import pytest


@pytest.mark.django_db()
def test_test_data_fixture() -> None:
    """This test ensures the test data fixture can be loaded successfully."""
    User.objects.create_user(username='test', password='test', id=1)
    call_command('loaddata', 'testdata')
