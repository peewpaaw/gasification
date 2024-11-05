import logging

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

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

ORDER_STATUSES = (
    (STATUS_CREATED, 'создана'),
    (STATUS_ACCEPTED, 'принята'),
    (STATUS_CANCELLED, 'отменена'),
    (STATUS_ON_CONFIRM, 'на согласовании'),
)

ALLOWED_STATUS_TRANSITIONS = {
    'created': ['accepted', 'cancelled', 'on_confirm'],
    'accepted': [],
    'cancelled': ['created'],
    'on_confirm': ['accepted', 'cancel']
}


class Order(BaseModel):
    construction_object = models.ForeignKey(ConstructionObject, on_delete=models.CASCADE)
    order_type = models.ForeignKey("OrderType", on_delete=models.CASCADE)
    status = models.CharField(choices=ORDER_STATUSES, default=STATUS_CREATED, max_length=100)
    on_date = models.DateField()
    applicant = models.CharField(max_length=255)
    employee = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name='related_orders'
    )

    def get_current_status(self):
        status_entry = OrderStatusHistory.objects.get_current(order=self.pk)
        return status_entry

    def change_status(self, status: ORDER_STATUSES, user):
        print('status update')
        try:
            current_status = self.get_current_status().status
            if status not in ALLOWED_STATUS_TRANSITIONS[current_status]:
                raise ValidationError(f"Invalid status transition: {current_status} -> {status}")

            OrderStatusHistory.objects.create(
                order=self,
                status=status,
                created_by=user,
            )
            print(f"Order model: status update: {status}")
        except ValidationError as e:
            logger.error(f"Order ID {self.id}: {str(e)}")

    def accept(self, user):
        current_status = self.get_current_status().status
        if current_status not in ('created',):
            raise ValidationError(f"Invalid status transition: {current_status} -> accepted")
        self._change_status(status='accepted', user=user)

    def _change_status(self, status: ORDER_STATUSES, user):
        OrderStatusHistory.objects.create(
            order=self,
            status=status,
            created_by=user,
        )

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'


class OrderStatusHistoryManager(models.Manager):
    def get_current(self, order: Order.pk):
        return self.filter(order=order).order_by('-created_at').first()


class OrderStatusHistory(BaseModel):
    order = models.ForeignKey("Order", on_delete=models.CASCADE)
    status = models.CharField(choices=ORDER_STATUSES, max_length=100)

    objects = OrderStatusHistoryManager()

    class Meta:
        verbose_name = 'Order statuses'
        verbose_name_plural = 'Order statuses'
