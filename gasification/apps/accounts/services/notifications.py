from apps.accounts.services.utils import get_signup_url
from apps.utils.email_messages import ClientEmailSignUpConfirm
from apps.accounts.models import TokenSignup


def send_signup_confirmation_email(token: TokenSignup) -> None:
    signup_url = f"{get_signup_url()}?token={token.key}"
    subject = "Регистрация в личном кабинете."
    context = {
        'account': token.user,
        'name': token.user.name,
        'email': token.user.email,
        'token': token.key,
        'signup_url': signup_url
    }
    email_message = ClientEmailSignUpConfirm(
        subject=subject,
        recipients=[token.user.email],
        **context
    )
    email_message.send_email()
