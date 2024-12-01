import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.erp.models import Counterparty


@pytest.fixture()
def api_client():
    return APIClient()


@pytest.fixture()
def client_user(db):
    counterparty_data = {
        'name': 'name',
        'inn': '1234567',
        'guid': 'guid',
    }
    counterparty = Counterparty.objects.create(**counterparty_data)
    data = {
        'login': 'client',
        'email': 'client@example.com',
        'password': 'password',
        'is_staff': False,
        'counterparty': counterparty,
    }
    return get_user_model().objects.create_user(**data)


@pytest.fixture()
def staff_user(db):
    data = {
        'login': 'staff',
        'email': 'staff@example.com',
        'password': 'password',
        'is_staff': True,
    }
    return get_user_model().objects.create(**data)


@pytest.fixture()
def api_client_as_staff(api_client, staff_user):
    api_client.force_authenticate(user=staff_user)
    return api_client


@pytest.fixture()
def api_client_as_client(api_client, client_user):
    api_client.force_authenticate(user=client_user)
    return api_client
