from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Order, OrderStatusHistory
from apps.orders.models import STATUS_ACCEPTED, STATUS_REJECTED, STATUS_AGREED



@receiver(post_save, sender=Order)
def create_initial_order_status(sender, instance, created, **kwargs):
    if created:
        OrderStatusHistory.objects.create(
            order=instance,
            status='created',
            created_by=instance.created_by

        )


@receiver(post_save, sender=OrderStatusHistory)
def update_order(sender, instance, created, **kwargs):
    if created:
        if instance.status == "accepted":
            pass
        elif instance.status == "agreed":
            pass
        handler = status_handlers.get(instance.status)
        if handler:
            handler(instance)


def handle_accepted(status_instance: OrderStatusHistory):
    order = status_instance.order
    order.on_date = status_instance.on_date
    order.employee = status_instance.created_by
    order.save()


def handle_agreed(status_instance: OrderStatusHistory):
    order = status_instance.order
    OrderStatusHistory.objects.create(
        order=order,
        status=STATUS_ACCEPTED,
        on_date=status_instance.on_date,
        created_by=status_instance.created_by
    )


def handle_rejected(status_instance: OrderStatusHistory):
    order = status_instance.order
    OrderStatusHistory.objects.create(
        order=order,
        status=STATUS_ACCEPTED,
        on_date=order.selected_date,
        created_by=status_instance.created_by
    )


status_handlers = {
    STATUS_ACCEPTED: handle_accepted,
    STATUS_AGREED: handle_agreed,
    STATUS_REJECTED: handle_rejected
}
