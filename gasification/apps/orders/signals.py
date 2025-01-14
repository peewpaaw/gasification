from django.db.models.signals import post_save
from django.db.transaction import on_commit
from django.dispatch import receiver

from .models import Order, OrderStatusHistory, STATUS_ON_CONFIRM, OrderConfig
from apps.orders.models import STATUS_ACCEPTED, STATUS_REJECTED, STATUS_AGREED
from .services.notifications import send_notification_status_transition


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
        on_commit(lambda: send_notification_status_transition(instance.status, instance.order))
        # if instance.status in OrderConfig.get_related_config().notification_on_statues:
        #     send_notification_status_transition(instance.status, instance.order)


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
