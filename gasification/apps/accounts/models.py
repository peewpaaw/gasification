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
