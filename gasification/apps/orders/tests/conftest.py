import pytest

from apps.erp.models import ConstructionObject, Counterparty
from apps.orders.models import OrderType, Order, OrderConfig


@pytest.fixture()
def construction_object(client_user):
    data = {
        "code": "code",
        "guid": "guid",
        "counterparty": client_user.counterparty
    }
    return ConstructionObject.objects.create(**data)


@pytest.fixture()
def order_type():
    data = {
        "order_type": "name",
        "guid": "guid"
    }
    return OrderType.objects.create(**data)


@pytest.fixture()
def order(construction_object, order_type, client_user):
    data = {
        "construction_object": construction_object,
        "applicant": "applicant",
        "order_type": order_type,
        "selected_date": "2024-01-01",
        "created_by": client_user
    }
    return Order.objects.create(**data)

@pytest.fixture()
def order_config(staff_user):
    data = {
        "order_count_per_day": 1,
        "order_count_friday": 1,
        "weekend_disabled": True,
        "time_start": "00:00",
        "time_end": "23:59",
        "created_by": staff_user,
    }
    return OrderConfig.objects.create(**data)
