from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse

from django_rest_passwordreset.signals import reset_password_token_created
from django.conf import settings

from apps.services.tasks import send_mail_message
from apps.accounts.models import TokenSignup
from apps.accounts.services.notifications import send_signup_confirmation_email, send_password_reset_confirmation_email


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """
    Handles password reset tokens
    """
    send_password_reset_confirmation_email(reset_password_token)
    # password_reset_url = settings.FRONTEND_PASSWORD_RESET_URL
    # if not password_reset_url:
    #     password_reset_url = instance.request.build_absolute_uri(
    #         reverse('password_reset:reset-password-confirm')
    #     )
    #
    # # send an e-mail to the user
    # context = {
    #     'current_user': reset_password_token.user,
    #     'username': reset_password_token.user.login,
    #     'email': reset_password_token.user.email,
    #     'token': reset_password_token.key,
    #     'reset_password_url': "{}?token={}".format(
    #         password_reset_url,
    #         reset_password_token.key)
    # }
    # subject = "Личный кабинет. Сброс пароля."
    # email_html_message = render_to_string('email/user_reset_password.html', context)
    # email_plaintext_message = render_to_string('email/user_reset_password.txt', context)
    # # create Celery task
    # send_mail_message.delay(title=subject,
    #                         message=email_plaintext_message,
    #                         content=email_html_message,
    #                         sender=settings.EMAIL_SENDER,
    #                         recipient=reset_password_token.user.email)


@receiver(post_save, sender=TokenSignup)
def account_token_signup_created(sender, instance, *args, **kwargs):
    """
    Handles sign-up tokens
    """
    send_signup_confirmation_email(instance)
