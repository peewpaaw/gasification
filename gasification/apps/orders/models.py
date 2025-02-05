import datetime
import logging

from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Subquery

from apps.erp.models import ConstructionObject
from apps.utils.models import BaseModel, BaseModelTimeAt

from core.settings import AUTH_USER_MODEL


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
    def _get_order_ids_in_status(self, statuses: []):
        latest_created_at_status_for_each_order = (OrderStatusHistory.objects
                                                   .values('order')
                                                   .annotate(max_created_at=models.Max('created_at')))
        if latest_created_at_status_for_each_order:
            max_created_at_values = latest_created_at_status_for_each_order.values('max_created_at')
            order_ids_with_status = (OrderStatusHistory.objects
                                     .filter(status__in=statuses, created_at__in=Subquery(max_created_at_values))
                                     .values_list('order', flat=True))
            return order_ids_with_status
        return []

    def get_by_statuses(self, statuses: []):
        return self.filter(pk__in=self._get_order_ids_in_status(statuses=statuses))


class Order(BaseModel):
    construction_object = models.ForeignKey(ConstructionObject, on_delete=models.PROTECT)
    order_type = models.ForeignKey("OrderType", on_delete=models.CASCADE)
    selected_date = models.DateField()
    applicant = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=13)

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
    time_start = models.TimeField(default=datetime.time(0, 0))
    time_end = models.TimeField(default=datetime.time(23, 59, 59))
    min_date = models.IntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ]
    )
    max_date = models.IntegerField(
        default=10,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ]
    )
    notification_on_statues = ArrayField(
        models.CharField(max_length=100, choices=ORDER_STATUSES),
        blank=True,
        null=True,
    )

    @staticmethod
    def get_related_config():
        return OrderConfig.objects.order_by('-created_at').first()

    class Meta:
        verbose_name = 'Config'
        verbose_name_plural = 'Config'


class OrderConfigException(BaseModel):
    on_date = models.DateField(unique=True)
    order_count_per_day = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'Config (exceptions)'
        verbose_name_plural = 'Config (exceptions)'
