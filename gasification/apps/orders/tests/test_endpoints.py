import datetime
import pytest
from django.urls import reverse

from apps.orders.models import Order


@pytest.mark.django_db
def test_order_list_as_unauth(api_client):
    """GET /orders/ as anonymous user"""
    url = reverse('orders-list')
    response = api_client.get(url)
    assert response.status_code == 401

@pytest.mark.django_db
def test_order_list(api_client_as_staff):
    """GET /orders/ as staff"""
    url = reverse('orders-list')
    response = api_client_as_staff.get(url)
    assert response.status_code == 200

@pytest.mark.django_db
def test_order_create_as_client(api_client_as_client, construction_object, order_type):
    """Create order by client"""
    order_data = {
        "construction_object": construction_object.id,
        "order_type": order_type.id,
        "selected_date": datetime.date.today(),
        "applicant": "applicant",
    }
    url = reverse('orders-list')
    response = api_client_as_client.post(url, data=order_data)
    assert response.status_code == 201
    assert Order.objects.count() == 1

def test_order_accept_as_client(api_client_as_client, order):
    """/orders/<pk>/accept by client"""
    url = reverse("orders-accept", args=[order.id])
    response = api_client_as_client.post(url)
    assert response.status_code == 403

def test_order_accept_as_staff(api_client_as_staff, order):
    """/orders/<pk>/accept by staff"""
    url = reverse("orders-accept", args=[order.id])
    response = api_client_as_staff.post(url)
    assert response.status_code == 200
