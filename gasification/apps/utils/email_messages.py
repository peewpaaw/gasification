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

    def __init__(self, recipients: [], **kwargs):
        self.recipients = recipients
        self.subject = self._get_subject()
        self.__dict__.update(kwargs)

    @abstractmethod
    def _get_subject(self):
        return ""

    @staticmethod
    def _get_sender():
        return settings.EMAIL_SENDER

    def _get_html_message(self):
        """Formats the contents of html into a string"""
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
        send_mail_message.delay(
            title=self._get_subject(),
            message="",
            content=self._get_html_message(),
            sender=self._get_sender(),
            recipient=self.recipients
        )
        self._send_log()


class ClientEmailStatusTransitionNotification(ClientEmailSender):
    """Class for sending email with status transition notification"""
    HTML_TEMPLATE = 'email/orders_notify_status_transition.html'
    LOG_NAME = 'Status Transition Notification'

    def _get_subject(self):
        return "УП «Мингаз». Изменение статуса заявки."


class ClientEmailSignUpConfirm(ClientEmailSender):
    """Class for sending email with sign up confirmation"""
    HTML_TEMPLATE = 'email/accounts_signup.html'
    LOG_NAME = 'Sign-Up Confirmation'

    def _get_subject(self):
        return "УП «Мингаз». Регистрация в личном кабинете."


class ClientEmailPasswordResetConfirm(ClientEmailSender):
    """Class for sending email with password reset confirmation"""
    HTML_TEMPLATE = 'email/user_reset_password.html'
    LOG_NAME = 'Password Reset Confirmation'

    def _get_subject(self):
        return "УП «Мингаз». Восстановления доступа."
