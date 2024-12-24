from django.conf import settings
from django.template.loader import render_to_string

from apps.services.tasks import send_mail_message

def send_notification_status_transition(status, order):
    context = {
        'name': order.created_by.name,
        'email': order.created_by.email,
        'url': settings.FRONTEND_URL,
        'construction_object_code': order.construction_object.code,
        'order_status': status,
        'order_id': order.id,
        'order_type': order.order_type.order_type,
    }
    subject = "УП `Мингаз`. Изменение статуса заявки."
    email_html_message = render_to_string('email/orders_notify_status_transition.html',
                                          context)
    # create Celery task
    send_mail_message.delay(title=subject,
                            message="",
                            content=email_html_message,
                            sender=settings.EMAIL_SENDER,
                            recipient=[order.created_by.email])