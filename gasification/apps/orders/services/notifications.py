from django.conf import settings

from apps.utils.email_messages import ClientEmailStatusTransitionNotification
from apps.orders.models import OrderConfig


def send_notification_status_transition(status, order):
    if not status in OrderConfig.get_related_config().notification_on_statues:
        return
    subject = "Изменение статуса заявки."
    context = {
        'name': order.created_by.name,
        'email': order.created_by.email,
        'url': settings.FRONTEND_URL,
        'construction_object_code': order.construction_object.code,
        'order_status': status,
        'order_id': order.id,
        'order_type': order.order_type.order_type,
    }
    email_message = ClientEmailStatusTransitionNotification(
        subject=subject,
        recipients=order.user.email,
        **context
    )
    email_message.send_email()
