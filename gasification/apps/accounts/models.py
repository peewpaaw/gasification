from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import gettext_lazy as _

from .managers import UserManager

from apps.erp.models import Counterparty


class User(AbstractBaseUser, PermissionsMixin):
    login = models.CharField(_('login'), max_length=100, unique=True)
    email = models.EmailField(_('email address'), blank=True, null=True)
    name = models.CharField(_('name'), max_length=150, blank=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    is_staff = models.BooleanField(_('is staff'), default=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_approved = models.BooleanField(_('is approved'), default=True)
    # only for clients
    counterparty = models.ForeignKey(Counterparty,
                                     on_delete=models.PROTECT,
                                     related_name='user',
                                     blank=True,
                                     null=True)

    objects = UserManager()

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        return self.name


class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client')
    counterparty = models.OneToOneField(Counterparty, on_delete=models.PROTECT, unique=True)

    objects = models.Manager()

    class Meta:
        verbose_name = _('Client profile')
        verbose_name_plural = _('Client profiles')


class TokenBaseModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(
        max_length=64,
        db_index=True,
        unique=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(
        default="",
        blank=True,
        null=True,
    )
    user_agent = models.CharField(
        max_length=512,
        default="",
        blank=True,
    )

    @staticmethod
    def generate_key():
        # generate the token using os.urandom and hexlify
        from apps.accounts.token import generate_token
        return generate_token()

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(TokenBaseModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class TokenSignup(TokenBaseModel):
    def __str__(self):
        return f"Password sign-up token for user {self.user}"

    class Meta:
        verbose_name = _('Token (Sign-up)')
        verbose_name_plural = _('Tokens (Sign-up)')
