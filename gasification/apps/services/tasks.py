from celery import shared_task
from django.core.mail import EmailMultiAlternatives

import logging

mail_logger = logging.getLogger('mail_notifications')

@shared_task
def test_task():
    print('test task')
    return 'hello from test task'


@shared_task
def send_mail_message(title, message, content, sender, recipient):
    mail_logger.info('Init mail: ')
    msg = EmailMultiAlternatives(
        subject=title,
        body=message,
        from_email=sender,
        to=recipient
    )
    msg.attach_alternative(content, "text/html")
    try:
        msg.send()
    except Exception as e:
        mail_logger.error(e)
