from django.contrib import admin

from .models import Counterparty, ConstructionObject


@admin.register(Counterparty)
class CounterpartyAdmin(admin.ModelAdmin):
    list_display = ('inn', 'name', 'guid')


@admin.register(ConstructionObject)
class ConstructionObjectAdmin(admin.ModelAdmin):
    list_display = ('counterparty', 'code', 'guid')
