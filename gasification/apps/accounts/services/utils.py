from django.conf import settings
from django.urls import reverse


def get_signup_url() -> str:
    """Returns the sign-up url"""
    signup_url = settings.FRONTEND_SIGNUP_URL
    if not signup_url:
        signup_url = f"{settings.BACKEND_URL}{reverse('signup')}"
    return signup_url

def get_password_reset_url() -> str:
    """Returns the password reset url"""
    password_reset_url = settings.FRONTEND_PASSWORD_RESET_URL
    if not password_reset_url:
        password_reset_url = f"{settings.BACKEND_URL}{reverse('password_reset:reset-password-confirm')}"
    return password_reset_url