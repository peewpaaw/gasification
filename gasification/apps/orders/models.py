from django.core.exceptions import ValidationError
from django.db import models

from apps.erp.models import ConstructionObject

from apps.utils.models import BaseModel, BaseModelTimeAt


class OrderType(BaseModelTimeAt):
    order_type = models.CharField(max_length=255)
    guid = models.CharField(max_length=36)

    def __str__(self):
        return self.order_type

    class Meta:
        verbose_name = 'Order type'
        verbose_name_plural = 'Order types'


ORDER_STATUSES = (
    ('created', 'создана'),
    ('accepted', 'принята'),
    ('cancelled', 'отменена'),
    ('on_confirm', 'на согласовании')  # перенос на дату?
)

# ALLOWED_STATUS_TRANSITIONS = {
#     'created': ['accepted', 'cancelled', 'on_confirm'],
#     'accepted': ['cancelled']
# }


class Order(BaseModel):
    construction_object = models.ForeignKey(ConstructionObject, on_delete=models.CASCADE)
    order_type = models.ForeignKey("OrderType", on_delete=models.CASCADE)
    on_date = models.DateField()
    applicant = models.CharField(max_length=255)

    def get_current_status(self):
        status_entry = OrderStatusHistory.objects.get_current(order=self.pk)
        return status_entry

    def accept(self, user):
        current_status = self.get_current_status().status
        if current_status not in ('created',):
            raise ValidationError(f"Invalid status transition: {current_status} -> accepted")
        self._change_status(status='accepted', user=user)

    def cancel(self, user):



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
