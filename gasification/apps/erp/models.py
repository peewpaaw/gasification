from django.contrib.postgres.fields import ArrayField
from django.db import models

from apps.utils.models import BaseModelTimeAt


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
    WORK_PACKAGES = (
        (1, 'ГСН (газопровод-ввод)'),
        (2, 'ГСН (участок газопровода)'),
        (3, 'ГСВ'),
    )
    counterparty = models.ForeignKey('Counterparty', on_delete=models.CASCADE)
    code = models.CharField(max_length=255)
    guid = models.CharField(max_length=36)
    address = models.CharField(max_length=255, blank=True, null=True)
    work_packages = ArrayField(
        models.SmallIntegerField(choices=WORK_PACKAGES),
        blank=True,
        null=True
    )

    def get_work_packages_display_list(self):
        if not self.work_packages:
            return []
        work_package_dict = dict(self.WORK_PACKAGES)
        return [work_package_dict[wp] for wp in self.work_packages if wp in work_package_dict]

    def __str__(self):
        return f"{self.code}"

    class Meta:
        verbose_name = 'Construction object'
        verbose_name_plural = 'Construction objects'
