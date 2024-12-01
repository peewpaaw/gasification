import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_accounts_me_as_unauth(api_client):
    """/accounts/me/ as anonymous user"""
    url = reverse('me')
    response = api_client.get(url)
    assert response.status_code == 401


@pytest.mark.django_db
def test_accounts_me_as_staff(api_client_as_staff):
    """/accounts/me/ as staff"""
    url = reverse('me')
    response = api_client_as_staff.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_accounts_me_as_client(api_client_as_staff):
    """/accounts/me/ as client"""
    url = reverse('me')
    response = api_client_as_staff.get(url)
    assert response.status_code == 200
