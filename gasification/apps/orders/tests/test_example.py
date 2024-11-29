from telnetlib import AUTHENTICATION

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.fixture()
def api_client():
    return APIClient()


@pytest.fixture()
def user_staff():
    data = {
        'login': 'staff',
        'email': 'staff@example.com',
        'password': 'password',
        'is_staff': True
    }
    return get_user_model().objects.create_user(**data)

@pytest.fixture()
def user_client():
    data = {
        'login': 'client',
        'email': 'client@example.com',
        'password': 'password',
        'is_staff': False
    }
    return get_user_model().objects.create_user(**data)

@pytest.fixture()
def staff_user_token(api_client, staff_user):
    payload = {
        'login': staff_user.login,
        'password': "password",
    }
    url = reverse('token_obtain_pair')
    response = api_client.post(url, data=payload)
    return response.json()['access']

def client_user_token(api_client):
    url = reverse('token_obtain_pair')
    
@pytest.mark.django_db
def test_orders_endpoints_unauth(api_client, staff_user):
    """Use fixture return value in a test."""
    url = reverse('orders-list')
    response = api_client.get(url)
    assert response.status_code == 401


@pytest.mark.django_db
def test_orders_list(api_client, staff_user_token):
    """Use fixture return value in a test."""
    url = reverse('orders-list')
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {staff_user_token}')
    print(staff_user_token)
    response = api_client.get(url)
    assert response.status_code == 200
