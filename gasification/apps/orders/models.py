import datetime
import logging

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models, transaction

from apps.erp.models import ConstructionObject
from apps.utils.models import BaseModel, BaseModelTimeAt


logger = logging.getLogger('order_status')


class OrderType(BaseModelTimeAt):
    order_type = models.CharField(max_length=255)
    guid = models.CharField(max_length=36)

    def __str__(self):
        return self.order_type

    class Meta:
        verbose_name = 'Order type'
        verbose_name_plural = 'Order types'


STATUS_CREATED = 'created'
STATUS_ACCEPTED = 'accepted'
STATUS_CANCELLED = 'cancelled'
STATUS_ON_CONFIRM = 'on_confirm'

STATUS_AGREED = 'agreed'
STATUS_REJECTED = 'rejected'

ORDER_STATUSES = (
    (STATUS_CREATED, 'создана'),
    (STATUS_ACCEPTED, 'принята'),
    (STATUS_CANCELLED, 'отменена'),
    (STATUS_ON_CONFIRM, 'на согласовании'),
)


class Order(BaseModel):
    construction_object = models.ForeignKey(ConstructionObject, on_delete=models.PROTECT)
    order_type = models.ForeignKey("OrderType", on_delete=models.CASCADE)
    selected_date = models.DateField()
    applicant = models.CharField(max_length=255)

    on_date = models.DateField()
    employee = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name='related_orders'
    )

    def get_related_status(self):
        return OrderStatusHistory.objects.filter(order=self).order_by('-created_at').first()

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'


class OrderStatusHistory(BaseModel):
    order = models.ForeignKey("Order", on_delete=models.CASCADE)
    status = models.CharField(choices=ORDER_STATUSES, max_length=100)
    on_date = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name = 'Order statuses'
        verbose_name_plural = 'Order statuses'
