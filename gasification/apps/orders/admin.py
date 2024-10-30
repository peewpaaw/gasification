from django.contrib import admin

from .models import OrderType, Order, OrderStatusHistory

# Register your models here.


class OrderStatusHistoryInlineAdmin(admin.StackedInline):
    model = OrderStatusHistory


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'status', 'created_at', 'created_by')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderStatusHistoryInlineAdmin]
    list_display = ('id', 'on_date', 'construction_object', 'order_type')


@admin.register(OrderType)
class OrderTypeAdmin(admin.ModelAdmin):
    list_display = ('order_type',)
