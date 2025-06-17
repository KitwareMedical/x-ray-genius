from django.contrib.auth.models import User
import pytest

from .factories import (
    CTInputFileFactory,
    InputParametersFactory,
    OutputImageFactory,
    SessionFactory,
    UserFactory,
)


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
def user_factory():
    return UserFactory


@pytest.fixture
def input_parameters_factory():
    return InputParametersFactory


@pytest.fixture
def session_factory():
    return SessionFactory


@pytest.fixture
def ct_input_file_factory():
    return CTInputFileFactory


@pytest.fixture
def output_image_factory():
    return OutputImageFactory
