from django.conf import settings
from django.urls import reverse


def get_signup_url() -> str:
    """Returns the sign-up url"""
    signup_url = settings.FRONTEND_SIGNUP_URL
    if not signup_url:
        signup_url = f"{settings.BACKEND_URL}{reverse('signup')}"
    return signup_url
