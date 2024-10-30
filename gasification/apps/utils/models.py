from django.contrib.auth import get_user_model
from django.db import models

from core.settings import AUTH_USER_MODEL


class BaseModelTimeAt(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseModelCreatedBy(models.Model):
    created_by = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_related",
    )
    #updated_by = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT)

    class Meta:
        abstract = True


class BaseModel(BaseModelTimeAt, BaseModelCreatedBy):
    class Meta:
        abstract = True
