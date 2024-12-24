import datetime
import pytest
from django.urls import reverse

from apps.orders.models import Order, OrderConfig, OrderConfigException


###############################
# TEST ORDER CONFIG ENDPOINTS #
###############################

@pytest.mark.django_db
def test_order_get_config_as_staff(api_client_as_staff):
    url = reverse("config")
    response = api_client_as_staff.get(url)
    assert response.status_code == 200

@pytest.mark.django_db
def test_order_get_config_as_client(api_client_as_client):
    url = reverse("config")
    response = api_client_as_client.get(url)
    assert response.status_code == 403

@pytest.mark.django_db
def test_order_set_config_as_staff(api_client_as_staff, order_config):
    config_init_count = OrderConfig.objects.all().count()
    data = {
        "order_count_per_day": 100,
        "order_count_friday": 100,
        "time_start": "14:00",
        "time_end": "15:00",
        "min_date": 0,
        "max_date": 10,
    }
    url = reverse("config")
    response = api_client_as_staff.put(url, data=data)
    assert response.status_code == 200
    assert config_init_count == OrderConfig.objects.all().count()


##########################################
# TEST ORDER CONFIG EXCEPTION ENDPOINTS  #
##########################################

def test_order_set_exception_as_staff(api_client_as_staff, order_config):
    data = {
        "on_date": "2024-01-01",
        "order_count_per_day": 0,
    }
    url = reverse("config-set-exception")
    response = api_client_as_staff.post(url, data=data)
    assert response.status_code == 200
    assert OrderConfigException.objects.all().count() == 1

def test_order_set_exception_as_client(api_client_as_client, order_config):
    data = {
        "on_date": "2024-01-01",
        "order_count_per_day": 0,
    }
    url = reverse("config-set-exception")
    response = api_client_as_client.post(url, data=data)
    assert response.status_code == 403


##########################################
# TEST ORDER CONFIG STATS ENDPOINTS  #
##########################################

@pytest.mark.django_db
def test_order_get_config_stats(api_client_as_staff, order_config):
    query_params = {
        "start_date": "2024-12-10",
        "end_date": "2024-12-20",
    }
    url = reverse("config-stats")
    response = api_client_as_staff.get(url, query_params=query_params)
    assert response.status_code == 200
    # in query_params we are trying to get 11 dates (2024-12-10 - 2024-12-20)
    assert len(response.json()['result']) == 11

def test_order_get_config_stats_as_client(api_client_as_client, order_config):
    query_params = {
        "start_date": "2024-01-01",
        "end_date": "2024-01-01",
    }
    url = reverse("config-stats")
    response = api_client_as_client.get(url, query_params=query_params)
    assert response.status_code == 403
