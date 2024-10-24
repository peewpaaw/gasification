from django.db import models


class BaseModelTimeAt(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Counterparty(BaseModelTimeAt):
    inn = models.CharField(max_length=12, unique=True)
    name = models.CharField(max_length=255)
    guid = models.CharField(max_length=36, unique=True)

    def __str__(self):
        return f"{self.name} ({self.inn})"

    class Meta:
        verbose_name = 'Counterparty'
        verbose_name_plural = 'Counterparties'


class ConstructionObject(BaseModelTimeAt):
    counterparty = models.ForeignKey('Counterparty', on_delete=models.CASCADE)
    code = models.CharField(max_length=255)
    guid = models.CharField(max_length=36)

    def __str__(self):
        return f"{self.code}"

    class Meta:
        verbose_name = 'Construction object'
        verbose_name_plural = 'Construction objects'
