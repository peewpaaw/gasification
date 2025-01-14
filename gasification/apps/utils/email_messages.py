import logging
from abc import ABC, abstractmethod

from django.conf import settings
from django.template.loader import render_to_string

from apps.services.tasks import send_mail_message


mail_logger = logging.getLogger('mail_notifications')


class ClientEmailSender(ABC):
    """Base class for sending emails"""
    HTML_TEMPLATE = ''
    LOG_NAME = ''

    def __init__(self, subject: str, recipients: [], **kwargs):
        self.sender = settings.EMAIL_SENDER
        self.url = settings.FRONTEND_URL
        self.subject = subject
        self.recipients = recipients
        self.__dict__.update(kwargs)

    def _get_html_message(self):
        """"""
        return render_to_string(self.HTML_TEMPLATE, self.__dict__)

    def _send_log(self):
        data = {
           "type": self.LOG_NAME,
           "recipients": self.recipients,
        }
        log_message = "Init email message: {0}".format(data)
        mail_logger.info(log_message)

    def send_email(self):
        """Send celery task"""
        send_mail_message.delay(title=self.subject,
                                message="",
                                content=self._get_html_message(),
                                sender=self.sender,
                                recipient=self.recipients)
        self._send_log()


class ClientEmailStatusTransitionNotification(ClientEmailSender):
    """Class for sending email with status transition notification"""
    HTML_TEMPLATE = 'email/orders_notify_status_transition.html'
    LOG_NAME = 'Status Transition Notification'


class ClientEmailSignUpConfirm(ClientEmailSender):
    """Class for sending email with sign up confirmation"""
    HTML_TEMPLATE = 'email/accounts_signup.html'
    LOG_NAME = 'Sign-Up Confirmation'


class ClientEmailPasswordResetConfirm(ClientEmailSender):
    """Class for sending email with password reset confirmation"""
    HTML_TEMPLATE = 'email/user_reset_password.html'
    LOG_NAME = 'Password Reset Confirmation'
