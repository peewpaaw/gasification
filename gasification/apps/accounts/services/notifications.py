from apps.accounts.services.utils import get_signup_url, get_password_reset_url
from apps.utils.email_messages import ClientEmailSignUpConfirm, ClientEmailPasswordResetConfirm
from apps.accounts.models import TokenSignup


def send_signup_confirmation_email(token: TokenSignup) -> None:
    signup_url = f"{get_signup_url()}?token={token.key}"
    context = {
        'account': token.user,
        'name': token.user.name,
        'email': token.user.email,
        'token': token.key,
        'signup_url': signup_url
    }
    email_message = ClientEmailSignUpConfirm(
        recipients=[token.user.email],
        **context
    )
    email_message.send_email()

def send_password_reset_confirmation_email(token) -> None:
    password_reset_url = f"{get_password_reset_url()}?token={token.key}"
    context = {
        'current_user': token.user,
        'name': token.user.name,
        'email': token.user.email,
        'token': token.key,
        'reset_password_url': password_reset_url
    }
    email_message = ClientEmailPasswordResetConfirm(
        recipients=[token.user.email],
        **context
    )
    email_message.send_email()
