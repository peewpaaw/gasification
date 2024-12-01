import pytest

from apps.erp.models import ConstructionObject, Counterparty
from apps.orders.models import OrderType, Order


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
