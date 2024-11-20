import logging

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Subquery

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


class OrderManager(models.Manager):
    def _get_order_ids_in_status(self, status):
        latest_created_at_status_for_each_order = (OrderStatusHistory.objects
                                                   .values('order')
                                                   .annotate(max_created_at=models.Max('created_at')))
        if latest_created_at_status_for_each_order:
            max_created_at_values = latest_created_at_status_for_each_order.values('max_created_at')
            order_ids_with_status = (OrderStatusHistory.objects
                                     .filter(status=status, created_at__in=Subquery(max_created_at_values))
                                     .values_list('order', flat=True))
            return order_ids_with_status
        return []

    def get_by_status(self, status):
        return self.filter(pk__in=self._get_order_ids_in_status(status=status))


class Order(BaseModel):
    construction_object = models.ForeignKey(ConstructionObject, on_delete=models.PROTECT)
    order_type = models.ForeignKey("OrderType", on_delete=models.CASCADE)
    selected_date = models.DateField()
    applicant = models.CharField(max_length=255)

    on_date = models.DateField(null=True, blank=True)
    employee = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name='related_orders'
    )
    objects = OrderManager()

    def get_related_status(self):
        return self.status_history.order_by('-created_at').first()

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'


class OrderStatusHistory(BaseModel):
    order = models.ForeignKey("Order", on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(choices=ORDER_STATUSES, max_length=100)
    on_date = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name = 'Order statuses'
        verbose_name_plural = 'Order statuses'


class OrderConfig(BaseModel):
    order_count_per_day = models.PositiveIntegerField()
    order_count_friday = models.PositiveIntegerField()
    weekend_disabled = models.BooleanField(default=True)
    updated_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'Config'
        verbose_name_plural = 'Config'


class OrderConfigException(BaseModel):
    on_date = models.DateField(unique=True)
    order_count_per_day = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'Config (exceptions)'
        verbose_name_plural = 'Config (exceptions)'
