"""Pytest configuration and fixtures."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from factory.django import DjangoModelFactory
from factory import Sequence, Faker


User = get_user_model()


class UserFactory(DjangoModelFactory):
    """Factory for creating test users."""

    class Meta:
        model = User

    email = Faker('email')
    username = Faker('user_name')
    first_name = 'Test'
    last_name = 'User'
    role = 'candidate'
    is_active = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override the default _create to set password."""
        password = kwargs.pop('password', 'testpassword123')
        obj = model_class(*args, **kwargs)
        obj.set_password(password)
        obj.save()
        return obj


class EmployerFactory(UserFactory):
    """Factory for creating employer users."""
    role = 'employer'
    company_name = Sequence(lambda n: f'Company {n}')
    is_approved_employer = True
    approval_status = 'approved'


@pytest.fixture
def api_client():
    """Provide API client."""
    return APIClient()


@pytest.fixture
def user(db):
    """Create a test user."""
    return UserFactory()


@pytest.fixture
def employer(db):
    """Create a test employer."""
    return EmployerFactory()


@pytest.fixture
def authenticated_client(api_client, user):
    """Provide authenticated API client."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def employer_client(api_client, employer):
    """Provide employer API client."""
    api_client.force_authenticate(user=employer)
    return api_client
